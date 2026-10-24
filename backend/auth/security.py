"""
Authentication and cryptographic utilities for FedSentinel.
"""

from __future__ import annotations

import hashlib
import secrets

from datetime import datetime
from datetime import timedelta
from datetime import timezone

import jwt

from pwdlib import PasswordHash


# ============================================================================
# Password hashing
# ============================================================================

password_hasher = PasswordHash.recommended()


def hash_password(
    password: str,
) -> str:
    """
    Securely hash a password.
    """

    return password_hasher.hash(
        password
    )


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a password against its stored hash.
    """

    return password_hasher.verify(
        password,
        password_hash,
    )


# ============================================================================
# Refresh tokens
# ============================================================================

def generate_refresh_token() -> str:
    """
    Generate a cryptographically secure refresh token.
    """

    return secrets.token_urlsafe(64)


def hash_refresh_token(
    token: str,
) -> str:
    """
    Hash the refresh token before database storage.

    The raw token is never stored.
    """

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ============================================================================
# Access tokens
# ============================================================================

def create_access_token(
    *,
    user_id: str,
    session_id: str,
    role: str,
    hospital_id: str | None,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    """
    Create a short-lived JWT access token.
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "sid": session_id,
        "role": role,
        "hospital_id": hospital_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=expires_minutes
        ),
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm,
    )


def decode_access_token(
    token: str,
    *,
    secret_key: str,
    algorithm: str,
) -> dict:
    """
    Decode and validate a JWT access token.
    """

    return jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
    )