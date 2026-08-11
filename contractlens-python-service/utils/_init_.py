# utils/__init__.py
# Makes 'utils' a proper Python package and exposes key functions.

from .extractor import extract_text, detect_clauses
from .summarizer import summarize_text, simplify_text

# ─── Aliases to match nlp_service.py import names ───────────────────────────
extract_text_from_file = extract_text
extract_clauses = detect_clauses

__all__ = [
    "extract_text",
    "extract_text_from_file",
    "detect_clauses",
    "extract_clauses",
    "summarize_text",
    "simplify_text",
]
