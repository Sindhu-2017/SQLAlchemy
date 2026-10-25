import asyncio
from typing import Any
import jwt
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.schemas.auth import RegisterRequest
from app.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)

class AuthenticationError(Exception):
    pass


class RegistrationConflict(Exception):
    pass

class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.refresh_tokens = RefreshTokenRepository(db)

    async def get_user_by_username(
        self,
        username: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(
        self,
        user_id: int,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def register(
        self,
        data: RegisterRequest,
    ) -> User:
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.username == data.username,
                    User.email == str(data.email),
                )
            )
        )
        if result.scalar_one_or_none() is not None:
            raise RegistrationConflict(
                "Username or email is already registered."
            )

        hashed_password = await asyncio.to_thread(
            hash_password,
            data.password
        )
        user = User(
            username=data.username,
            email=str(data.email),
            hashed_password=hashed_password,
            role="user",
            is_active=True,
        )
        self.db.add(user)

        try:
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError as exc:
            await self.db.rollback()
            raise RegistrationConflict(
                "Username or email is already registered."
            ) from exc

        return user

    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> User:
        user = await self.get_user_by_username(username)
        if user is None:
            raise AuthenticationError(
                "Invalid username or password."
            )
        password_is_valid = await asyncio.to_thread(
            verify_password,
            password,
            user.hashed_password,
        )
        if not password_is_valid or not user.is_active:
            raise AuthenticationError(
                "Invalid username or password."
            )
        return user

    async def issue_tokens(
        self,
        user_id: int,
        role: str,
    ) -> dict[str, str]:
        access_token = create_access_token(
            user_id=user_id,
            role=role,
        )

        refresh_token, jti, expires_at = create_refresh_token(
            user_id=user_id,
            role=role,
        )

        token_record = RefreshToken(
            jti=jti,
            token_hash=hash_refresh_token(refresh_token),
            user_id=user_id,
            expires_at=expires_at,
            revoked=False,
        )
        await self.refresh_tokens.create(token_record)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def login(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        try:
            user = await self.authenticate(username, password)
            tokens = await self.issue_tokens(
                user_id=user.user_id,
                role=user.role,
            )
            await self.db.commit()
            return tokens

        except Exception:
            await self.db.rollback()
            raise

    async def refresh(
        self,
        raw_refresh_token: str,
    ) -> dict[str, str]:
        try:
            payload = decode_token(raw_refresh_token)

            if payload.get("type") != "refresh":
                raise AuthenticationError(
                    "Invalid or expired refresh token."
                )
            user_id = int(payload["sub"])
            jti = payload["jti"]

            if not isinstance(jti, str):
                raise AuthenticationError(
                    "Invalid or expired refresh token."
                )
            token_record = await self.refresh_tokens.get_valid(
                jti=jti,
                user_id=user_id,
                token_hash=hash_refresh_token(
                    raw_refresh_token
                ),
            )
            if token_record is None:
                raise AuthenticationError(
                    "Invalid or expired refresh token."
                )

            user = await self.get_user_by_id(user_id)

            if user is None or not user.is_active:
                raise AuthenticationError(
                    "Invalid or expired refresh token."
                )

            await self.refresh_tokens.revoke(token_record)

            tokens = await self.issue_tokens(
                user_id=user.user_id,
                role=user.role,
            )
            await self.db.commit()
            return tokens

        except (
            jwt.InvalidTokenError,
            ValueError,
            TypeError,
            KeyError,
            AuthenticationError,
        ) as exc:
            await self.db.rollback()
            if isinstance(exc, AuthenticationError):
                raise
            raise AuthenticationError(
                "Invalid or expired refresh token."
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    async def logout(
        self,
        raw_refresh_token: str,
        user_id: int,
    ) -> None:
        try:
            payload = decode_token(raw_refresh_token)
            if payload.get("type") != "refresh":
                raise AuthenticationError(
                    "Invalid refresh token."
                )

            token_user_id = int(payload["sub"])
            jti = payload["jti"]

            if token_user_id != user_id or not isinstance(jti, str):
                raise AuthenticationError(
                    "Invalid refresh token."
                )

            token_record = await self.refresh_tokens.get_valid(
                jti=jti,
                user_id=user_id,
                token_hash=hash_refresh_token(
                    raw_refresh_token
                ),
            )
            if token_record is not None:
                await self.refresh_tokens.revoke(token_record)
                await self.db.commit()

        except (
            jwt.InvalidTokenError,
            ValueError,
            TypeError,
            KeyError,
            AuthenticationError,
        ) as exc:
            await self.db.rollback()

            if isinstance(exc, AuthenticationError):
                raise

            raise AuthenticationError(
                "Invalid refresh token."
            ) from exc

        except Exception:
            await self.db.rollback()
            raise

    async def get_user_from_token(
        self,
        payload: dict[str, Any],
    ) -> User:
        try:
            user_id = int(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise AuthenticationError(
                "Invalid authentication token."
            ) from exc

        user = await self.get_user_by_id(user_id)

        if user is None or not user.is_active:
            raise AuthenticationError(
                "Invalid authentication token."
            )
        return user