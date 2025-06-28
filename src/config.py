from __future__ import annotations

from pathlib import Path
from functools import lru_cache
import os
import yaml
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Path to config.yaml at repo root
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a symmetric key from ``password`` and ``salt`` using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(password.encode())


def encrypt_config(password: str, salt: bytes, data: bytes) -> bytes:
    """Encrypt configuration data using a password and salt."""
    key = derive_key(password, salt)
    return Fernet(base64.urlsafe_b64encode(key)).encrypt(data)

class ConfigValidationError(Exception):
    """Raised when ``config.yaml`` contains invalid data."""


@lru_cache(maxsize=1)
def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    data = CONFIG_PATH.read_bytes()
    key = os.getenv("CONFIG_KEY")
    salt = os.getenv("CONFIG_SALT", "static_salt").encode()
    if key:
        derived = derive_key(key, salt)
        cipher = Fernet(base64.urlsafe_b64encode(derived))
        try:
            data = cipher.decrypt(data)
        except Exception as exc:
            raise RuntimeError("Failed to decrypt config") from exc
    try:
        return yaml.safe_load(data) or {}
    except yaml.YAMLError as exc:
        raise ConfigValidationError(f"Invalid YAML: {exc}") from exc
