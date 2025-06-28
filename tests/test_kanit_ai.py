import pytest

jinja2 = pytest.importorskip('jinja2')
pdfkit = pytest.importorskip('pdfkit')

from assistant.kanit_ai.veri_etiketi_okuyucu import read_label_mapping
from assistant.kanit_ai.bakim_log_analiz import detect_fake_maintenance
from assistant.kanit_ai.sozlesme_uretici import create_contract
from assistant.kanit_ai.acil_durum_raporu import generate_emergency_report


def test_read_label_mapping(tmp_path):
    csv = tmp_path / "labels.csv"
    csv.write_text("serial,replacement\nA1,B1\n")
    mapping = read_label_mapping(csv)
    assert mapping == {"A1": "B1"}


def test_detect_fake_maintenance():
    logs = ["ok", "ok", "placeholder entry"]
    result = detect_fake_maintenance(logs)
    assert "placeholder entry" in result
    assert "ok" in result


def test_create_contract(tmp_path):
    pdf = tmp_path / "out.pdf"
    create_contract(["madde 1", "madde 2"], str(pdf))
    assert pdf.is_file()


def test_generate_emergency_report():
    text = generate_emergency_report({"sorumlu": "Ali"})
    assert "Ali" in text
