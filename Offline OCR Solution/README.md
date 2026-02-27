# ⌶ Offline OCR Solution

Fully offline text extraction from images — no API keys, no internet required.

## Engines

| Engine | Strength | System dep |
|--------|----------|-----------|
| **Tesseract** | Fast, great for clean printed text | `apt install tesseract-ocr` |
| **EasyOCR** | Deep-learning, handles handwriting + mixed scripts | None (downloads model ~100MB) |
| **Auto** | Runs both, returns highest confidence result | Either or both |

## Setup

```bash
pip install -r requirements.txt

# Tesseract engine (recommended for speed)
sudo apt install tesseract-ocr          # Ubuntu/Debian
brew install tesseract                  # macOS
# Windows: https://github.com/UB-Mannheim/tesseract/wiki

# Extra language packs (optional)
sudo apt install tesseract-ocr-fra tesseract-ocr-deu  # French, German
```

## Usage

### 1. Web UI + API (recommended)
```bash
uvicorn api.main:app --reload --port 8000
# Open http://localhost:8000
```

### 2. CLI
```bash
# Basic
python ocr_cli.py image.png

# With options
python ocr_cli.py invoice.png --engine tesseract --lang eng --extract --out result.txt

# Full JSON output
python ocr_cli.py scan.jpg --engine easyocr --json

# Check available engines
python ocr_cli.py --engines
```

### 3. API directly
```bash
# Upload image
curl -X POST http://localhost:8000/ocr/upload \
  -F "file=@invoice.png" \
  -F "engine=auto" \
  -F "lang=eng" \
  -F "enhance=true" \
  -F "extract=true"

# Base64
curl -X POST http://localhost:8000/ocr/base64 \
  -H "Content-Type: application/json" \
  -d '{"image_b64": "<base64>", "engine": "auto"}'

# Engine status
curl http://localhost:8000/ocr/engines
```

## Project Structure

```
ocr-solution/
├── core/
│   ├── engine.py        # Tesseract + EasyOCR wrappers, image preprocessing
│   └── postprocess.py   # Text cleaning, entity extraction (emails, dates...)
├── api/
│   └── main.py          # FastAPI: /ocr/upload, /ocr/base64, /ocr/engines
├── frontend/
│   └── index.html       # Drag-and-drop UI, tabs: text / smart extract / preview
├── ocr_cli.py           # CLI tool
└── requirements.txt
```

## API Response

```json
{
  "engine":     "tesseract",
  "text":       "Invoice #1042\nDate: 2024-01-15\nTotal: $1,250.00",
  "confidence": 94.2,
  "time_ms":    380,
  "lines":      ["Invoice #1042", "Date: 2024-01-15", "Total: $1,250.00"],
  "words":      [...],
  "preview_b64": "...",
  "extracted": {
    "doc_type":   "invoice",
    "word_count": 6,
    "line_count": 3,
    "emails":     [],
    "dates":      ["2024-01-15"],
    "amounts":    ["$1,250.00"],
    "phones":     [],
    "urls":       []
  }
}
```

## Preprocessing Pipeline

Every image goes through:
1. Upscale if smaller than 1000px (OCR accuracy improves at higher resolution)
2. Sharpen filter
3. Contrast enhancement (1.5×)
4. Grayscale + adaptive threshold (binarization)

Toggle with `enhance=false` if your image is already clean.
