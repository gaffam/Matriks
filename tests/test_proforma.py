import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

pytest.importorskip('jinja2')
from proforma_engine import create_quote

def test_create_quote():
    quote = create_quote("2 kamera")
    assert quote["toplam"] >= 0

def test_parse_request_flexible():
    from proforma_engine import parse_request
    items = parse_request("5 adet kamera, 2 tane dvr")
    assert any(it.name == "kamera" and it.quantity == 5 for it in items)
    assert any(it.name == "dvr" and it.quantity == 2 for it in items)
