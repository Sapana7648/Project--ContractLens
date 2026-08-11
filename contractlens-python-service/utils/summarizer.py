import re
from collections import Counter

# ─── Store last extracted text for re-summarize/simplify ───────────────────
_last_text = ""

def summarize_text(text: str) -> str:
    """
    Extractive summarization — no ML model needed.
    Picks the most important sentences based on word frequency.
    """
    global _last_text
    _last_text = text

    if not text or len(text.strip()) < 50:
        return "Document is too short to summarize."

    try:
        sentences = _split_sentences(text)
        if len(sentences) <= 3:
            return " ".join(sentences)

        scores = _score_sentences(sentences)
        top_n = max(3, min(8, len(sentences) // 4))
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_indices = sorted([i for i, _ in ranked[:top_n]])
        summary = " ".join(sentences[i] for i in top_indices)
        return summary

    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return f"Summarization failed: {str(e)}"

def simplify_text(text: str) -> str:
    """
    Plain-English version — shorter extractive summary
    focused on the first and most frequent sentences.
    """
    global _last_text
    source = _last_text if _last_text else text

    if not source or len(source.strip()) < 50:
        return "Document is too short to simplify."

    try:
        sentences = _split_sentences(source)
        if len(sentences) <= 2:
            return " ".join(sentences)

        scores = _score_sentences(sentences)
        top_n = max(2, min(4, len(sentences) // 6))
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_indices = sorted([i for i, _ in ranked[:top_n]])
        simplified = " ".join(sentences[i] for i in top_indices)
        return simplified

    except Exception as e:
        print(f"❌ Simplification error: {e}")
        return f"Simplification failed: {str(e)}"

# ─── Helpers ────────────────────────────────────────────────────────────────

def _split_sentences(text: str) -> list:
    """Split text into clean sentences."""
    text = re.sub(r'\s+', ' ', text).strip()
    raw = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw if len(s.strip()) > 20]

def _score_sentences(sentences: list) -> dict:
    """Score sentences by word frequency (TF-style)."""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'shall', 'this',
        'that', 'these', 'those', 'it', 'its', 'as', 'if', 'not', 'no',
        'any', 'all', 'each', 'both', 'such', 'than', 'then', 'so', 'yet'
    }

    # Count word frequencies
    words = re.findall(r'\b[a-z]{3,}\b', ' '.join(sentences).lower())
    freq = Counter(w for w in words if w not in stop_words)

    # Score each sentence
    scores = {}
    for i, sentence in enumerate(sentences):
        sentence_words = re.findall(r'\b[a-z]{3,}\b', sentence.lower())
        score = sum(freq.get(w, 0) for w in sentence_words if w not in stop_words)
        # Normalize by sentence length to avoid bias toward long sentences
        scores[i] = score / max(len(sentence_words), 1)

    return scores