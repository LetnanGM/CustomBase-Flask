"""
fingerprint.py — Request fingerprinting utilities.
"""

import hashlib


def generate(ip: str, user_agent: str = "", endpoint: str = "", method: str = "") -> str:
    """Generate a short fingerprint from request metadata."""
    raw = f"{user_agent}|{endpoint}|{method}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]
