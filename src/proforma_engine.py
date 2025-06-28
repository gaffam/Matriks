"""Basit proforma teklifi hesaplama modulu.

Fiyat listesi ``data/price_list.csv`` dosyasindan okunur. Dosya ``item,price``
baslikli bir CSV olup, kod u run-time'da bu listeyi bellege aktarir.

Modul ayrica teklif bilgilerini PDF'e d\u00f6kebilmek i\u00e7in yardimci fonksiyon
saglar. PDF olusturmada ``jinja2`` ve ``pdfkit`` kullanilir.
"""

from dataclasses import dataclass
from pathlib import Path
import csv
from typing import Dict, List
import re
import logging

from jinja2 import Template
import pdfkit

# Fiyatlar bu sozlukte tutulur ve uygulama acilirken CSV'den okunur.
PRICE_LIST: Dict[str, float] = {}

# CSV dosyasinin yolu.
PRICE_CSV = Path(__file__).resolve().parent.parent / "data" / "price_list.csv"


def _load_prices(csv_path: Path) -> Dict[str, float]:
    prices: Dict[str, float] = {}
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    prices[row["item"]] = float(row["price"])
                except (KeyError, ValueError):
                    continue
    return prices


# CSV'den fiyatlari yukle
PRICE_LIST.update(_load_prices(PRICE_CSV))


@dataclass
class ProformaItem:
    name: str
    quantity: int

    def total(self) -> float:
        price = PRICE_LIST.get(self.name, 0)
        return price * self.quantity


_REQ_RE = re.compile(r"(\d+)\s*(?:adet|tane)?\s*([\w_]+)")


def parse_request(request: str) -> List[ProformaItem]:
    """Parse one or more ``ProformaItem`` from text like ``'4 kamera, 1 dvr'``."""
    items: List[ProformaItem] = []
    for qty, name in _REQ_RE.findall(request.lower()):
        items.append(ProformaItem(name=name, quantity=int(qty)))

    if not items and request.strip():
        items.append(ProformaItem(name=request.strip().split()[-1], quantity=1))

    return items


def create_quote(request: str) -> Dict[str, object]:
    """Parse request and compute totals for each product."""
    try:
        items = parse_request(request)
    except Exception as exc:
        logging.error("proforma parse failed: %s", exc)
        raise ValueError("Gecersiz istek") from exc
    if not items:
        raise ValueError("Urun belirtilmedi")
    item_list = [
        {"urun": it.name, "adet": it.quantity, "tutar": it.total()} for it in items
    ]
    toplam = sum(it["tutar"] for it in item_list)
    return {"kalemler": item_list, "toplam": toplam}


def quote_to_pdf(quote: Dict[str, object], dest: str) -> str:
    """Basit bir PDF proforma dosyasi olusturur.

    Parameters
    ----------
    quote : Dict[str, float]
        ``create_quote`` cikti sozlugu.
    dest : str
        Olusacak PDF dosyasi yolu.
    """

    template = Template(
        """
        <h1>Proforma Teklif</h1>
        <table border="1" cellspacing="0" cellpadding="4">
        {% for it in kalemler %}
            <tr><td>{{ it.urun }}</td><td>{{ it.adet }}</td><td>{{ it.tutar }} TL</td></tr>
        {% endfor %}
        </table>
        <p><strong>Toplam: {{ toplam }} TL</strong></p>
        """
    )
    html = template.render(**quote)
    pdfkit.from_string(html, dest)
    return dest


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: proforma_engine.py '<adet> <urun>'")
        raise SystemExit(1)
    print(create_quote(" ".join(sys.argv[1:])))
