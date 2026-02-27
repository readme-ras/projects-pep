"""
Offline OCR Engine
──────────────────
Two engines available:
  • tesseract  — fast, great for printed text, needs tesseract binary
  • easyocr    — deep-learning based, better for handwriting/mixed scripts
  • auto       — tries both, returns best result (by confidence)

Image preprocessing pipeline:
  denoise → deskew → threshold → upscale → contrast enhance
"""

import io
import base64
import time
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

# ── Lazy imports (user may not have all engines) ───────────────────────────────

def _try_import_tesseract():
    try:
        import pytesseract
        pytesseract.get_tesseract_version()   # raises if binary missing
        return pytesseract
    except Exception:
        return None

def _try_import_easyocr():
    try:
        import easyocr
        return easyocr
    except ImportError:
        return None


# ── Image preprocessing ────────────────────────────────────────────────────────

def preprocess(img: Image.Image, enhance: bool = True) -> Image.Image:
    """Apply a standard preprocessing pipeline to improve OCR accuracy."""

    # 1. Convert to RGB if needed
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # 2. Upscale small images (OCR works best at 300+ DPI equivalent)
    w, h = img.size
    if max(w, h) < 1000:
        scale = 2.0
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    if enhance:
        # 3. Sharpen
        img = img.filter(ImageFilter.SHARPEN)

        # 4. Contrast enhancement
        img = ImageEnhance.Contrast(img).enhance(1.5)

        # 5. Convert to grayscale for thresholding
        gray = img.convert("L")

        # 6. Adaptive threshold via numpy
        arr = np.array(gray)
        threshold = arr.mean() * 0.85
        binary = np.where(arr > threshold, 255, 0).astype(np.uint8)
        img = Image.fromarray(binary).convert("RGB")

    return img


def pil_to_b64(img: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode()


# ── Tesseract engine ───────────────────────────────────────────────────────────

class TesseractEngine:
    name = "tesseract"

    def __init__(self):
        self._pytesseract = _try_import_tesseract()
        self.available = self._pytesseract is not None

    def extract(self, img: Image.Image, lang: str = "eng", psm: int = 3) -> dict:
        if not self.available:
            return {"error": "Tesseract not installed. Run: pip install pytesseract && apt install tesseract-ocr"}

        pt = self._pytesseract
        config = f"--psm {psm}"

        t0 = time.perf_counter()
        text = pt.image_to_string(img, lang=lang, config=config)

        # Get per-word confidence data
        try:
            data = pt.image_to_data(img, lang=lang, config=config,
                                     output_type=pt.Output.DICT)
            confidences = [c for c in data["conf"] if c != -1]
            avg_conf = round(sum(confidences) / len(confidences), 1) if confidences else 0.0
            words = [
                {"text": data["text"][i], "conf": data["conf"][i],
                 "x": data["left"][i], "y": data["top"][i],
                 "w": data["width"][i], "h": data["height"][i]}
                for i in range(len(data["text"]))
                if data["text"][i].strip() and data["conf"][i] > 0
            ]
        except Exception:
            avg_conf = 0.0
            words    = []

        elapsed = time.perf_counter() - t0
        return {
            "engine":     "tesseract",
            "text":       text.strip(),
            "confidence": avg_conf,
            "words":      words,
            "time_ms":    round(elapsed * 1000),
            "lang":       lang,
        }


# ── EasyOCR engine ─────────────────────────────────────────────────────────────

class EasyOCREngine:
    name = "easyocr"
    _reader_cache: dict = {}

    def __init__(self):
        self._easyocr = _try_import_easyocr()
        self.available = self._easyocr is not None

    def _get_reader(self, langs: list[str]):
        key = ",".join(sorted(langs))
        if key not in self._reader_cache:
            self._reader_cache[key] = self._easyocr.Reader(langs, gpu=_has_gpu())
        return self._reader_cache[key]

    def extract(self, img: Image.Image, langs: list[str] = None) -> dict:
        if not self.available:
            return {"error": "EasyOCR not installed. Run: pip install easyocr"}

        langs = langs or ["en"]
        reader = self._get_reader(langs)

        arr = np.array(img)
        t0  = time.perf_counter()
        results = reader.readtext(arr, detail=1, paragraph=False)
        elapsed = time.perf_counter() - t0

        words = []
        full_text_parts = []
        confidences = []
        for (bbox, text, conf) in results:
            words.append({
                "text": text,
                "conf": round(conf * 100, 1),
                "bbox": [[int(p[0]), int(p[1])] for p in bbox],
            })
            full_text_parts.append(text)
            confidences.append(conf)

        avg_conf = round((sum(confidences) / len(confidences)) * 100, 1) if confidences else 0.0

        return {
            "engine":     "easyocr",
            "text":       " ".join(full_text_parts),
            "confidence": avg_conf,
            "words":      words,
            "time_ms":    round(elapsed * 1000),
            "langs":      langs,
        }


def _has_gpu() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# ── Auto engine (tries both, picks best) ──────────────────────────────────────

class AutoEngine:
    name = "auto"

    def __init__(self):
        self.tesseract = TesseractEngine()
        self.easyocr   = EasyOCREngine()
        self.available = self.tesseract.available or self.easyocr.available

    def extract(self, img: Image.Image, **kwargs) -> dict:
        results = []
        if self.tesseract.available:
            r = self.tesseract.extract(img, **{k: v for k, v in kwargs.items() if k in ("lang", "psm")})
            if "error" not in r:
                results.append(r)
        if self.easyocr.available:
            r = self.easyocr.extract(img, **{k: v for k, v in kwargs.items() if k in ("langs",)})
            if "error" not in r:
                results.append(r)

        if not results:
            return {"error": "No OCR engine available. Install tesseract or easyocr."}

        best = max(results, key=lambda x: x.get("confidence", 0))
        best["all_results"] = results
        return best


# ── Public factory ─────────────────────────────────────────────────────────────

_engines = {
    "tesseract": TesseractEngine(),
    "easyocr":   EasyOCREngine(),
    "auto":      AutoEngine(),
}

def get_engine(name: str = "auto"):
    return _engines.get(name, _engines["auto"])

def available_engines() -> dict:
    return {name: eng.available for name, eng in _engines.items() if name != "auto"}
