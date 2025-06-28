"""Simple offline data sync placeholder."""

from pathlib import Path
import json
import requests

API_URL = "http://localhost:8000/upload"  # placeholder
def sync_data() -> None:
    """Synchronize local changes with the server when online."""
    # Placeholder for future implementation

    upload_pending_data()


def upload_pending_data() -> None:
    """Upload JSON files in ``pending_uploads`` directory."""
    pending_dir = Path("pending_uploads")
    for file in pending_dir.glob("*.json"):
        try:
            requests.post(API_URL, json=json.loads(file.read_text()))
            file.unlink()
        except Exception:
            continue
