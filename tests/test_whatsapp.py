from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

pytest.importorskip('requests')
from unittest.mock import patch
from speech.whatsapp_integration import process_whatsapp_audio

@patch('requests.get')
def test_whatsapp_audio(mock_get):
    mock_get.return_value.content = b'fake_audio'
    result = process_whatsapp_audio('http://fake.url')
    assert isinstance(result, str)
