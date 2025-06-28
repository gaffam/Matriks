import sqlite3
from pathlib import Path
from config import load_config

CFG = load_config()
DB_PATH = Path(__file__).resolve().parent.parent / CFG.get("paths", {}).get("prompt_cache", "prompt_cache.db")


class PromptCache:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS cache (prompt TEXT PRIMARY KEY, answer TEXT)"
            )

    def get(self, prompt: str) -> str | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT answer FROM cache WHERE prompt=?", (prompt,)
            ).fetchone()
            return row[0] if row else None

    def set(self, prompt: str, answer: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache(prompt, answer) VALUES (?, ?)", (prompt, answer)
            )

    def backup(self, backup_path: str) -> None:
        """Copy the cache database to ``backup_path``."""
        from shutil import copy2

        copy2(self.db_path, backup_path)

