import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.config.settings import get_settings


settings = get_settings()

password_hash = PasswordHash.recommended()

DUMMY_PASSWORD_HASH = password_hash.hash(
    "DummyPasswordForTimingOnly@123"
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_token(
    user_id: int,
    role: str,
    token_type: str,
    expires_delta: timedelta,
) -> tuple[str, str, datetime]:
   
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    jti = str(uuid.uuid4())

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    return token, jti, expires_at


def create_access_token(
    user_id: int,
    role: str,
) -> str:

    token, _, _ = create_token(
        user_id=user_id,
        role=role,
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        ),
    )

    return token


def create_refresh_token(
    user_id: int,
    role: str,
) -> tuple[str, str, datetime]:

    return create_token(
        user_id=user_id,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.refresh_token_expire_days
        ),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        options={
            "require": [
                "sub",
                "exp",
                "iat",
                "jti",
                "type",
            ],
        },
    )


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()