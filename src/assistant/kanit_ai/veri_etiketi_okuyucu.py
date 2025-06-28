"""Seri numarasi ve degisim eslestirme araci."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict


def read_label_mapping(csv_path: str | Path) -> Dict[str, str]:
    """Parse a CSV containing serial numbers and replacement numbers.

    The CSV is expected to have two columns: ``serial`` and ``replacement``.
    Returns a dict mapping serial -> replacement.
    """
    path = Path(csv_path)
    mapping: Dict[str, str] = {}
    if not path.is_file():
        raise FileNotFoundError(f"Label file not found: {csv_path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            serial = row.get("serial")
            repl = row.get("replacement")
            if serial and repl:
                mapping[serial.strip()] = repl.strip()
    return mapping
