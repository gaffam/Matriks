"""WhatsApp audio handler using Twilio or WhatsApp Business API."""

from typing import Optional
from pathlib import Path
import requests

from .speech_client import transcribe


def download_audio(url: str, dest: Optional[str] = None) -> str:
    """Download audio file and return local path."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    if dest is None:
        dest = Path("/tmp") / Path(url).name
    with open(dest, "wb") as fh:
        fh.write(resp.content)
    return str(dest)


def process_whatsapp_audio(audio_url: str, lang: str | None = None) -> str:
    path = download_audio(audio_url)
    return transcribe(path, lang=lang)
