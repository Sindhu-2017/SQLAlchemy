from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash
from app.config.settings import get_settings

settings = get_settings()
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify( plain_password, hashed_password )


def create_access_token(
    user_id: int,
    role: str,
) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expires_at
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
        options={
            "require": [
                "sub",
                "exp",
                "iat",
                "type",
            ],
        }
    )