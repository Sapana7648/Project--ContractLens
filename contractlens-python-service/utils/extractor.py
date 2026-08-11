import os
import fitz          # PyMuPDF
import docx

def extract_text(file_path: str) -> str:
    """
    Extract text from PDF, DOCX, or TXT files.
    Returns extracted text as a string.
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            return _extract_pdf(file_path)
        elif ext == ".docx":
            return _extract_docx(file_path)
        elif ext == ".txt":
            return _extract_txt(file_path)
        else:
            return f"Unsupported file type: {ext}"
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return f"Could not extract text: {str(e)}"

# ─── Alias (required by nlp_service.py) ─────────────────────────────────────
def extract_text_from_file(file_path: str) -> str:
    """Alias for extract_text — used by nlp_service.py"""
    return extract_text(file_path)

def _extract_pdf(path: str) -> str:
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def _extract_docx(path: str) -> str:
    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()

def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def detect_clauses(text: str) -> list:
    """
    Detect common legal clauses in the text.
    Returns a list of clause dicts with title, severity, color, description, excerpt.
    """
    clause_patterns = [
        {
            "title": "Confidentiality",
            "keywords": ["confidential", "non-disclosure", "nda", "proprietary", "trade secret"],
            "severity": "High",
            "color": "#4361ee",
            "description": "Restricts sharing of sensitive information between parties."
        },
        {
            "title": "Termination",
            "keywords": ["terminat", "cancel", "end of agreement", "expir", "notice of termination"],
            "severity": "Critical",
            "color": "#e63946",
            "description": "Defines conditions under which the contract can be ended."
        },
        {
            "title": "Liability",
            "keywords": ["liabilit", "indemnif", "damages", "liable", "hold harmless"],
            "severity": "Critical",
            "color": "#f4a261",
            "description": "Outlines financial responsibility and damage limitations."
        },
        {
            "title": "Payment Terms",
            "keywords": ["payment", "invoice", "fee", "compensation", "due date", "billing"],
            "severity": "High",
            "color": "#2a9d8f",
            "description": "Specifies payment schedules, amounts, and methods."
        },
        {
            "title": "Intellectual Property",
            "keywords": ["intellectual property", "copyright", "patent", "trademark", "ownership of work"],
            "severity": "High",
            "color": "#7209b7",
            "description": "Defines ownership of creative works and inventions."
        },
        {
            "title": "Governing Law",
            "keywords": ["governing law", "jurisdiction", "applicable law", "dispute resolution"],
            "severity": "Medium",
            "color": "#3a86ff",
            "description": "Specifies which legal system governs the contract."
        },
        {
            "title": "Non-Compete",
            "keywords": ["non-compete", "non compete", "competitive activity", "restraint of trade"],
            "severity": "High",
            "color": "#ff6b6b",
            "description": "Prevents parties from engaging in competing activities."
        },
        {
            "title": "Force Majeure",
            "keywords": ["force majeure", "act of god", "unforeseeable", "beyond control"],
            "severity": "Medium",
            "color": "#06d6a0",
            "description": "Excuses performance when extraordinary events occur."
        },
    ]

    text_lower = text.lower()
    detected = []

    for clause in clause_patterns:
        for keyword in clause["keywords"]:
            if keyword in text_lower:
                # Find excerpt
                idx = text_lower.find(keyword)
                start = max(0, idx - 40)
                end = min(len(text), idx + 120)
                excerpt = text[start:end].replace("\n", " ").strip()

                detected.append({
                    "title": clause["title"],
                    "severity": clause["severity"],
                    "color": clause["color"],
                    "description": clause["description"],
                    "excerpt": excerpt,
                })
                break  # Only add each clause type once

    return detected

# ─── Alias (required by nlp_service.py) ─────────────────────────────────────
def extract_clauses(text: str) -> list:
    """Alias for detect_clauses — used by nlp_service.py"""
    return detect_clauses(text)