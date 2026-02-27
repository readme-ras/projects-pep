"""
FastAPI OCR API — fully offline, no external services.

POST /ocr/upload    — process image file upload
POST /ocr/base64    — process base64-encoded image
GET  /ocr/engines   — list available engines
GET  /               — serve frontend
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import io
import base64
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from PIL import Image

from core.engine import get_engine, available_engines, preprocess, pil_to_b64
from core.postprocess import clean_text, extract_data

app = FastAPI(
    title="Offline OCR API",
    description="Local OCR powered by Tesseract + EasyOCR — no internet required.",
    version="1.0.0",
)

# Serve frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
static_dir   = os.path.join(frontend_dir, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ── Schemas ────────────────────────────────────────────────────────────────────

class Base64Request(BaseModel):
    image_b64:   str
    engine:      str = "auto"
    lang:        str = "eng"
    enhance:     bool = True
    extract:     bool = True

    model_config = {"json_schema_extra": {"example": {
        "image_b64": "<base64 encoded image>",
        "engine":    "auto",
        "lang":      "eng",
        "enhance":   True,
        "extract":   True,
    }}}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run_ocr(img: Image.Image, engine_name: str, lang: str, enhance: bool, do_extract: bool) -> dict:
    processed = preprocess(img, enhance=enhance)
    engine    = get_engine(engine_name)

    if not engine.available and engine_name != "auto":
        raise HTTPException(
            status_code=503,
            detail=f"Engine '{engine_name}' not available. Check installation.",
        )

    # Run OCR
    kwargs = {"lang": lang} if engine_name == "tesseract" else {"langs": [lang]}
    if engine_name == "auto":
        kwargs = {"lang": lang, "langs": [lang]}

    result = engine.extract(processed, **kwargs)

    if "error" in result:
        raise HTTPException(status_code=503, detail=result["error"])

    # Post-process
    result["text"]  = clean_text(result.get("text", ""))
    result["lines"] = result["text"].split("\n")

    if do_extract:
        ed = extract_data(result["text"])
        result["extracted"] = ed.to_dict()

    # Include preprocessed image as b64 for UI preview
    result["preview_b64"] = pil_to_b64(processed)

    return result


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return HTMLResponse("<h1>OCR API running — visit /docs</h1>")


@app.get("/ocr/engines")
def list_engines():
    """List available OCR engines and their status."""
    engines = available_engines()
    return {
        "engines":    engines,
        "any_available": any(engines.values()),
        "recommended": "auto",
    }


@app.post("/ocr/upload")
async def ocr_upload(
    file:    UploadFile = File(...),
    engine:  str  = Form(default="auto"),
    lang:    str  = Form(default="eng"),
    enhance: bool = Form(default=True),
    extract: bool = Form(default=True),
):
    """Upload an image file and extract text."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    contents = await file.read()
    try:
        img = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot open image file.")

    result = _run_ocr(img, engine, lang, enhance, extract)
    result["filename"] = file.filename
    result["size"]     = {"width": img.width, "height": img.height}
    return result


@app.post("/ocr/base64")
def ocr_base64(body: Base64Request):
    """Extract text from a base64-encoded image."""
    try:
        data = base64.b64decode(body.image_b64)
        img  = Image.open(io.BytesIO(data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data.")

    result = _run_ocr(img, body.engine, body.lang, body.enhance, body.extract)
    result["size"] = {"width": img.width, "height": img.height}
    return result


@app.get("/health")
def health():
    engines = available_engines()
    return {
        "status":  "ok",
        "engines": engines,
        "any_ready": any(engines.values()),
    }
