"""Language detection helper."""

from langdetect import detect


def detect_lang(text: str) -> str:
    """Return ISO language code for ``text``."""
    try:
        return detect(text)
    except Exception:
        return "en"
