"""Text-to-speech using Piper or another command line TTS tool."""

import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Optional
import logging

from gtts import gTTS
from playsound import playsound

from config import load_config

CFG = load_config()
PIPER_CMD = CFG.get("paths", {}).get("piper_binary", "piper")


def _ensure_cmd(cmd: str) -> bool:
    """Return True if ``cmd`` exists on PATH."""
    return shutil.which(cmd) is not None


def speak(text: str, voice: Optional[str] = None, lang: str = "tr") -> None:
    """Speak ``text`` using either Piper or gTTS as fallback."""
    if _ensure_cmd(PIPER_CMD):
        cmd = [PIPER_CMD, "--input", text]
        if voice:
            cmd.extend(["--voice", voice])
        subprocess.run(cmd, check=False)
        return
    logging.warning("%s not found, using gTTS fallback", PIPER_CMD)

    # Fallback to gTTS
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        audio_path = tmp.name
    try:
        playsound(audio_path)
    finally:
        Path(audio_path).unlink(missing_ok=True)


if __name__ == "__main__":
    import sys

if len(sys.argv) < 2:
    print("Usage: voice_response.py <text> [voice] [lang]")
    raise SystemExit(1)
text = sys.argv[1]
voice = sys.argv[2] if len(sys.argv) > 2 else None
lang = sys.argv[3] if len(sys.argv) > 3 else "tr"
speak(text, voice=voice, lang=lang)
