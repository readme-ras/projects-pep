"""
Post-processing utilities for OCR output.
  - clean_text   : strip noise, normalise whitespace
  - detect_type  : infer document type (invoice, receipt, form, plain)
  - extract_data : pull structured data (dates, numbers, emails, etc.)
"""

import re
from dataclasses import dataclass, field


# ── Text cleaning ──────────────────────────────────────────────────────────────

def clean_text(raw: str) -> str:
    """Remove common OCR artefacts and normalise whitespace."""
    text = raw

    # Remove null bytes / control chars
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalise quotes
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing whitespace per line
    lines = [ln.rstrip() for ln in text.split("\n")]
    text  = "\n".join(lines).strip()

    return text


# ── Data extraction ────────────────────────────────────────────────────────────

@dataclass
class ExtractedData:
    emails:       list[str] = field(default_factory=list)
    phones:       list[str] = field(default_factory=list)
    dates:        list[str] = field(default_factory=list)
    amounts:      list[str] = field(default_factory=list)
    urls:         list[str] = field(default_factory=list)
    numbers:      list[str] = field(default_factory=list)
    doc_type:     str       = "unknown"
    word_count:   int       = 0
    char_count:   int       = 0
    line_count:   int       = 0

    def to_dict(self) -> dict:
        return {
            "doc_type":   self.doc_type,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "line_count": self.line_count,
            "emails":     self.emails,
            "phones":     self.phones,
            "dates":      self.dates,
            "amounts":    self.amounts,
            "urls":       self.urls,
            "numbers":    self.numbers,
        }


_EMAIL_RE   = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE   = re.compile(r"(?:\+?\d[\d\s\-().]{7,}\d)")
_DATE_RE    = re.compile(
    r"\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}"
    r"|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)
_AMOUNT_RE  = re.compile(r"[$€£¥₹]\s?\d[\d,]*\.?\d*|\d[\d,]*\.?\d*\s?(?:USD|EUR|GBP|INR)")
_URL_RE     = re.compile(r"https?://[^\s]+|www\.[^\s]+")
_NUMBER_RE  = re.compile(r"\b\d{4,}\b")

_INVOICE_WORDS = {"invoice", "total", "amount due", "subtotal", "bill to", "tax", "vat"}
_RECEIPT_WORDS = {"receipt", "thank you", "cashier", "change", "tender", "item"}
_FORM_WORDS    = {"name:", "date:", "signature", "check", "form", "field", "fill"}


def extract_data(text: str) -> ExtractedData:
    lower = text.lower()
    ed = ExtractedData()

    ed.emails   = list(dict.fromkeys(_EMAIL_RE.findall(text)))
    ed.phones   = list(dict.fromkeys(_PHONE_RE.findall(text)))[:5]
    ed.dates    = list(dict.fromkeys(_DATE_RE.findall(text)))
    ed.amounts  = list(dict.fromkeys(_AMOUNT_RE.findall(text)))
    ed.urls     = list(dict.fromkeys(_URL_RE.findall(text)))
    ed.numbers  = list(dict.fromkeys(_NUMBER_RE.findall(text)))[:10]

    ed.word_count = len(text.split())
    ed.char_count = len(text)
    ed.line_count = text.count("\n") + 1

    # Detect document type
    if sum(1 for w in _INVOICE_WORDS if w in lower) >= 2:
        ed.doc_type = "invoice"
    elif sum(1 for w in _RECEIPT_WORDS if w in lower) >= 2:
        ed.doc_type = "receipt"
    elif sum(1 for w in _FORM_WORDS if w in lower) >= 2:
        ed.doc_type = "form"
    elif ed.word_count > 100:
        ed.doc_type = "document"
    else:
        ed.doc_type = "text"

    return ed
