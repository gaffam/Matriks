"""Madde madde PDF sozlesme ureticisi."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import jinja2
import pdfkit

DEFAULT_TEMPLATE = """
<html><body>
<h1>Sözleşme</h1>
<ol>
{% for item in clauses %}<li>{{ item }}</li>{% endfor %}
</ol>
</body></html>
"""


def create_contract(clauses: Iterable[str], output_pdf: str, template: str | None = None) -> None:
    """Create a PDF contract from clauses."""
    tpl = jinja2.Template(template or DEFAULT_TEMPLATE)
    html = tpl.render(clauses=list(clauses))
    pdfkit.from_string(html, output_pdf)
    if not Path(output_pdf).is_file():
        raise RuntimeError("PDF could not be created")
