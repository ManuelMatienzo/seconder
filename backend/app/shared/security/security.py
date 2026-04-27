from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from types import SimpleNamespace
from typing import Any

import bcrypt as bcrypt_backend
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 260000

if not hasattr(bcrypt_backend, "__about__"):
    bcrypt_backend.__about__ = SimpleNamespace(__version__=bcrypt_backend.__version__)

_bcrypt_hashpw = bcrypt_backend.hashpw


def _passlib_compatible_hashpw(password: bytes, salt: bytes) -> bytes:
    return _bcrypt_hashpw(password[:72], salt)


bcrypt_backend.hashpw = _passlib_compatible_hashpw
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_legacy_password(password: str, stored_hash: str) -> bool:
    return _verify_pbkdf2_password(password, stored_hash)


def _verify_pbkdf2_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != PASSWORD_HASH_ALGORITHM:
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)


def verify_password(password: str, stored_hash: str) -> bool:
    if stored_hash.startswith(f"{PASSWORD_HASH_ALGORITHM}$"):
        return _verify_legacy_password(password, stored_hash)

    return pwd_context.verify(password, stored_hash)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ValueError("Token invalido o expirado") from exc
