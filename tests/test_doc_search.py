import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

pytest.importorskip('yaml')
from doc_search import search


def test_doc_search_fuzzy():
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)
    sample = docs_dir / 'manual.txt'
    sample.write_text('Panel acil durdugu anda baglantilari kontrol edin')
    result = search('panel durdu ne yapmali')
    assert 'baglantilari' in result
