"""Bakim loglarini sahte islemler icin analiz eder."""

from __future__ import annotations

from typing import Iterable, List


def detect_fake_maintenance(lines: Iterable[str]) -> List[str]:
    """Return a list of suspicious log lines.

    A log line is flagged if it contains duplicated entries or unexpected
    keywords like "placeholder" indicating incomplete forms.
    """
    seen = set()
    suspects: List[str] = []
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if clean in seen or "placeholder" in clean.lower():
            suspects.append(clean)
        else:
            seen.add(clean)
    return suspects
