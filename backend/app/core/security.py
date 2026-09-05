"""Password hashing and JWT encode/decode — the only place either happens.

Never log a raw password or a token anywhere near this module (TDD §19).
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return _pwd_context.verify(plain_password, password_hash)


class InvalidTokenError(Exception):
    pass


def create_access_token(
    *, subject: str, role: str, secret_key: str, algorithm: str, expires_minutes: int
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str, *, secret_key: str, algorithm: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc
