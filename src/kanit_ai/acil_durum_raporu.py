"""Olay sonrasi sorumluluk dagilimini olusturur."""

from __future__ import annotations

from typing import Dict

import jinja2

REPORT_TEMPLATE = """
Olay Sonrasi Sorumluluk Dagilimi
================================
{% for key, value in details.items() %}
- **{{ key }}**: {{ value }}
{% endfor %}
"""


def generate_emergency_report(details: Dict[str, str]) -> str:
    """Return a formatted text report."""
    tpl = jinja2.Template(REPORT_TEMPLATE)
    return tpl.render(details=details)
