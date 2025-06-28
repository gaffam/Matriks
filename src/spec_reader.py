"""Parse tender specification files and extract equipment counts and staff info."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Dict

SPEC_PATTERNS = {
    "kamera": r"(\d+)\s*(?:adet)?\s*kamera",
    "personel": r"(\d+)\s*personel",
}

def parse_spec(path: str | Path) -> Dict[str, int]:
    text = Path(path).read_text(encoding="utf-8")
    result: Dict[str, int] = {}
    for key, pattern in SPEC_PATTERNS.items():
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            result[key] = int(m.group(1))
    return result
