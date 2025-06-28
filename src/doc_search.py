from __future__ import annotations

"""Simple text-based document search for retrieval-augmented answers."""

from pathlib import Path
from difflib import SequenceMatcher
from collections import Counter
from config import load_config

CFG = load_config()
DOCS_DIR = Path(__file__).resolve().parent.parent / CFG.get("paths", {}).get("docs_dir", "docs")


def _vec(text: str) -> Counter:
    words = [w.lower() for w in text.split()]
    return Counter(words)


def _jaccard(a: Counter, b: Counter) -> float:
    intersection = sum((a & b).values())
    union = sum((a | b).values())
    return intersection / union if union else 0.0


def search(question: str) -> str | None:
    """Return a relevant line from the docs using simple vector similarity."""
    query_vec = _vec(question)
    best_line: str | None = None
    best_score = 0.0
    for path in DOCS_DIR.glob("**/*.txt"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            score = _jaccard(query_vec, _vec(line))
            if score > best_score:
                best_score = score
                best_line = line.strip()
    if best_score < 0.1:
        # Fallback to fuzzy matching
        query = question.lower()
        best_line = None
        best_score = 0.0
        for path in DOCS_DIR.glob("**/*.txt"):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for line in text.splitlines():
                score = SequenceMatcher(None, query, line.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_line = line.strip()
    return best_line
