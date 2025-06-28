import pytest
from pathlib import Path

torch = pytest.importorskip('torch')
from assistant.invoice_parser import InvoiceParser

invoice2data = pytest.importorskip('invoice2data')

SAMPLE_PDF = Path(__file__).parent / 'sample_invoice.pdf'

@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason='sample pdf missing')
def test_parse_pdf(tmp_path):
    parser = InvoiceParser()
    data = parser.parse_invoice(str(SAMPLE_PDF))
    assert isinstance(data, dict)


def test_missing_file():
    parser = InvoiceParser()
    with pytest.raises(FileNotFoundError):
        parser.parse_invoice('nofile.png')
