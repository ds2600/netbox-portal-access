from __future__ import annotations
import json
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

MASK = "**********"

def _get_key() -> bytes:
    key = (
        getattr(settings, "PLUGINS_CONFIG", {})
        .get("netbox_portal_access", {})
        .get("fernet_key")
    )
    if not key:
        raise RuntimeError("Fernet key not found in settings.")

    if isinstance(key, str):
        key = key.encode()
    return key

def get_fernet() -> Fernet:
    return Fernet(_get_key())

def encrypt_json(data: dict) -> str:
    token = get_fernet().encrypt(json.dumps(data).encode("utf-8"))
    return token.decode("utf-8")

def decrypt_json(token: str | None) -> dict:
    if not token:
        return {}
    try:
        raw = get_fernet().decrypt(token.encode("utf-8"))
        return json.loads(raw.decode("utf-8"))
    except (InvalidToken, ValueError):
        return {}

def mask(value: str | None) -> str:
    return MASK if value else ""


