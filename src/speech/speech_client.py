"""Simple wrapper around whisper.cpp for offline STT.

This module provides two helpers:

``transcribe``   – transcribe an existing audio file.
``transcribe_mic`` – record a short snippet from the microphone and
pass it to ``transcribe``.  This is handy on Android devices running
the Kivy GUI where the user wants to talk directly to the assistant.

The code expects the ``whisper`` binary from ``whisper.cpp`` to be
available on the ``PATH`` unless a different location is specified in
``config.yaml``.
"""

import os
import subprocess
import shutil
import tempfile
from typing import Optional
from pathlib import Path

import speech_recognition as sr

from utils.config import load_config

try:
    import whisper as whisper_torch
except Exception:  # if not installed
    whisper_torch = None

CFG = load_config()
WHISPER_CMD = CFG.get("paths", {}).get("whisper_binary", "whisper")


def _ensure_cmd(cmd: str) -> None:
    if shutil.which(cmd) is None:
        raise RuntimeError(
            f"{cmd} not found. Please install whisper.cpp or update config.yaml"
        )


def transcribe(audio_path: str, model_path: Optional[str] = None, lang: str | None = None) -> str:
    """Transcribe ``audio_path`` using whisper.cpp.

    Parameters
    ----------
    audio_path: str
        Path to the audio file.
    model_path: str, optional
        Path to the Whisper model. If omitted the default model is used.
    """
    if not Path(audio_path).exists():
        raise FileNotFoundError(audio_path)
    try:
        _ensure_cmd(WHISPER_CMD)
        cmd = [WHISPER_CMD, audio_path]
        if lang:
            cmd.extend(["-l", lang])
        if model_path:
            cmd.extend(["-m", model_path])
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.stdout.strip()
    except RuntimeError:
        if whisper_torch is None:
            raise
        import logging
        logging.warning("%s not found, falling back to openai-whisper", WHISPER_CMD)
        model = whisper_torch.load_model("base" if model_path is None else model_path)
        result = model.transcribe(audio_path, language=lang)
        return result.get("text", "").strip()


def transcribe_mic(duration: int = 5, model_path: Optional[str] = None, lang: str | None = None) -> str:
    """Record from the default microphone and transcribe the snippet.

    Parameters
    ----------
    duration: int
        Duration of the recording in seconds.
    model_path: str, optional
        Optional whisper model path.
    """

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.record(source, duration=duration)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio.get_wav_data())
        tmp_path = tmp.name

    try:
        return transcribe(tmp_path, model_path, lang)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: speech_client.py <audio_file> [model_path] [lang]")
        sys.exit(1)
    audio = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else None
    lang = sys.argv[3] if len(sys.argv) > 3 else None
    print(transcribe(audio, model, lang))
