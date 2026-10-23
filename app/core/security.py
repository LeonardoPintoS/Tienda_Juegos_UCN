from __future__ import annotations

import bcrypt

_ENCODING = "utf-8"


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with bcrypt. Never store the plain value."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode(_ENCODING), salt)
    return hashed.decode(_ENCODING)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode(_ENCODING), password_hash.encode(_ENCODING))
