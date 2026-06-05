"""
Wathiq — Crypto utilities for PII encryption and hashing.
"""
import hashlib
import hmac
import os


def hash_sha256(data: str) -> str:
    """SHA-256 hash of string. Used for document integrity proofs."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def hash_api_key(key: str) -> str:
    """Hash an API key for storage (never store raw keys)."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def verify_api_key(key: str, key_hash: str) -> bool:
    """Verify a raw API key against its stored hash."""
    return hash_api_key(key) == key_hash


def generate_api_key() -> tuple[str, str]:
    """Generate (raw_key, key_prefix). Return raw key to user, store hash."""
    raw = os.urandom(32).hex()
    prefix = raw[:8]
    return raw, prefix


def hmac_sign(payload: str, secret: str) -> str:
    """HMAC-SHA256 sign a payload. Used for API request signing."""
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def hmac_verify(payload: str, signature: str, secret: str) -> bool:
    """Verify an HMAC-SHA256 signature."""
    expected = hmac_sign(payload, secret)
    return hmac.compare_digest(expected, signature)