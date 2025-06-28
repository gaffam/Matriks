from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

fastapi = pytest.importorskip('fastapi')
from fastapi.testclient import TestClient
from api_server import app, llm_client

client = TestClient(app)

def test_api_ask():
    # ensure startup ran
    assert llm_client is not None
    resp = client.post('/ask', json={'prompt': 'Kod 135 nedir?'})
    assert resp.status_code == 200
    assert 'answer' in resp.json()
