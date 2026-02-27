#!/usr/bin/env python3
"""
ocr_cli.py — Quick offline OCR from the terminal.

Usage:
  python ocr_cli.py image.png
  python ocr_cli.py image.jpg --engine tesseract --lang eng
  python ocr_cli.py invoice.png --extract --out result.txt
  python ocr_cli.py scan.pdf --engine easyocr
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image
from core.engine import get_engine, available_engines, preprocess
from core.postprocess import clean_text, extract_data

# ── ANSI ────────────────────────────────────────────────────────────────────────
R = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
YEL = "\033[93m"; GRN = "\033[92m"; RED = "\033[91m"; CYA = "\033[96m"

def c(text, *codes): return "".join(codes) + str(text) + R
def hr(n=60): return c("─" * n, CYA)


def main():
    parser = argparse.ArgumentParser(description="Offline OCR — Tesseract + EasyOCR")
    parser.add_argument("image",          help="Path to image file")
    parser.add_argument("--engine", "-e", default="auto",
                        choices=["auto", "tesseract", "easyocr"],
                        help="OCR engine to use (default: auto)")
    parser.add_argument("--lang",   "-l", default="eng",
                        help="Language code (default: eng)")
    parser.add_argument("--no-enhance",   action="store_true",
                        help="Skip image preprocessing")
    parser.add_argument("--extract", "-x", action="store_true",
                        help="Extract entities (emails, dates, amounts...)")
    parser.add_argument("--out",    "-o",  default=None,
                        help="Save extracted text to file")
    parser.add_argument("--json",         action="store_true",
                        help="Output full JSON result")
    parser.add_argument("--engines",      action="store_true",
                        help="List available engines and exit")
    args = parser.parse_args()

    if args.engines:
        engines = available_engines()
        print(f"\n{c('Available OCR engines:', BOLD)}")
        for name, avail in engines.items():
            status = c("✅ available", GRN) if avail else c("❌ not installed", RED)
            print(f"  {c(name, YEL)} — {status}")
        print()
        return

    # Load image
    if not os.path.exists(args.image):
        print(c(f"❌ File not found: {args.image}", RED))
        sys.exit(1)

    print(f"\n{c('⌶ OCR Engine', BOLD, CYA)} — offline\n")
    print(f"  File   : {c(args.image, YEL)}")
    print(f"  Engine : {c(args.engine, YEL)}")
    print(f"  Lang   : {c(args.lang, YEL)}")

    try:
        img = Image.open(args.image)
    except Exception as e:
        print(c(f"❌ Cannot open image: {e}", RED))
        sys.exit(1)

    print(f"  Size   : {c(f'{img.width}×{img.height}', DIM)}")

    # Preprocess
    enhance = not args.no_enhance
    if enhance:
        print(f"\n  {c('Preprocessing image...', DIM)}", end=" ", flush=True)
        img = preprocess(img, enhance=True)
        print(c("done", GRN))

    # Run OCR
    print(f"  {c('Running OCR...', DIM)}", end=" ", flush=True)
    engine = get_engine(args.engine)
    if not engine.available:
        print(c(f"\n❌ Engine '{args.engine}' not available.", RED))
        engines = available_engines()
        avail = [k for k, v in engines.items() if v]
        if avail:
            print(c(f"   Try: --engine {avail[0]}", YEL))
        sys.exit(1)

    kwargs = {}
    if args.engine == "tesseract":
        kwargs = {"lang": args.lang}
    elif args.engine == "easyocr":
        kwargs = {"langs": [args.lang]}
    else:
        kwargs = {"lang": args.lang, "langs": [args.lang]}

    result = engine.extract(img, **kwargs)

    if "error" in result:
        print(c(f"\n❌ {result['error']}", RED))
        sys.exit(1)

    print(c("done", GRN))

    # Clean
    text = clean_text(result.get("text", ""))

    # Output
    print(f"\n{hr()}")
    print(c("  EXTRACTED TEXT", BOLD))
    print(hr())
    print(text if text.strip() else c("  (no text detected)", DIM))
    print(hr())

    # Stats
    print(f"\n  {c('Confidence', BOLD)} : {c(f\"{result.get('confidence', 0):.1f}%\", YEL)}")
    print(f"  {c('Engine    ', BOLD)} : {c(result.get('engine', '?'), YEL)}")
    print(f"  {c('Time      ', BOLD)} : {c(f\"{result.get('time_ms', 0)} ms\", YEL)}")

    # Entity extraction
    if args.extract and text:
        print(f"\n{hr()}")
        print(c("  EXTRACTED ENTITIES", BOLD))
        print(hr())
        ed = extract_data(text)
        d  = ed.to_dict()
        for key in ("doc_type", "word_count", "line_count", "emails",
                    "phones", "dates", "amounts", "urls"):
            val = d.get(key)
            if val and val not in (0, []):
                print(f"  {c(key.ljust(12), DIM)}: {c(val, GRN)}")

    # Save
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n  {c('✅ Saved to', GRN)} {c(args.out, YEL)}")

    # JSON dump
    if args.json:
        import json
        result["text"] = text
        if args.extract:
            result["extracted"] = extract_data(text).to_dict()
        print(f"\n{hr()}")
        print(c("  JSON RESULT", BOLD))
        print(hr())
        print(json.dumps(result, indent=2, default=str))

    print()


if __name__ == "__main__":
    main()
