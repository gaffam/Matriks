import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

pytest.importorskip('llama_cpp')
from assistant.ask_llm import LLMClient


def test_llm_response_quality():
    client = LLMClient()
    response = client.ask('Yangin butonu ariza kodu nedir?')
    assert '135' in response
