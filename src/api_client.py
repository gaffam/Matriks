import os
import requests
from config import load_config

CFG = load_config()
SETTINGS = CFG.get("api_settings", {})
BASE_URL = SETTINGS.get("base_url")
TOKEN = os.getenv("API_TOKEN") or SETTINGS.get("api_token")


def ask_cloud(query: str) -> str:
    if not BASE_URL:
        raise RuntimeError("API base URL not configured")
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    try:
        resp = requests.post(f"{BASE_URL}/ask", json={"prompt": query}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("answer", "")
    except Exception as exc:
        raise RuntimeError(f"API request failed: {exc}") from exc
