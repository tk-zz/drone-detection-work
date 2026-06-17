from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from backend.core.constants import TOKEN_HOURS


def utc_now():
    return datetime.now(timezone.utc)


def iso_now():
    return utc_now().isoformat()


def hash_password(password: str, salt: str | None = None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return salt, digest.hex()


def verify_password(password: str, salt: str, password_hash: str):
    _, candidate = hash_password(password, salt)
    return hmac.compare_digest(candidate, password_hash)


def create_token_expiry():
    now = utc_now()
    return now, now + timedelta(hours=TOKEN_HOURS)


def create_session_token():
    return secrets.token_urlsafe(32)
