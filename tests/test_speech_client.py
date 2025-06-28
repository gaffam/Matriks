import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

pytest.importorskip('speech_recognition')
from speech_client import transcribe


def test_invalid_audio_file():
    with pytest.raises(FileNotFoundError):
        transcribe('nonexistent.wav')
