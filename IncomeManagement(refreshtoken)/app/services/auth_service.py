from typing import Any
import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.interfaces.refresh_token_repository import (
    RefreshTokenRepositoryInterface
)
from app.repositories.interfaces.user_repository import (
    UserRepositoryInterface
)
from app.schemas.auth import RegisterRequest
from app.exceptions.income_exceptions import (
    AuthenticationError,
    RegistrationConflict
)

class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepositoryInterface,
        refresh_token_repository: RefreshTokenRepositoryInterface
    ) -> None:
        self.db = db
        self.users = user_repository
        self.refresh_tokens = refresh_token_repository

    async def register(self, data: RegisterRequest) -> User:
        existing_user = await self.users.get_by_username_or_email(
            username=data.username,
            email=str(data.email),
        )

        if existing_user is not None:
            if existing_user.username == data.username:
                raise RegistrationConflict(
                    "Username is already registered."
                )
            raise RegistrationConflict("Email is already registered.")

        user = User(
            username=data.username,
            email=str(data.email),
            hashed_password=hash_password(data.password),
            role="user",
            is_active=True,
        )

        try:
            await self.users.create(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError as exc:
            await self.db.rollback()
            raise RegistrationConflict(
                "Username or email is already registered."
            ) from exc
        except Exception:
            await self.db.rollback()
            raise

    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> User:
        user = await self.users.get_by_username_or_email(
            username=username
        )

        if user is None:
            raise AuthenticationError(
                "Invalid username or password."
            )

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise AuthenticationError("This account is inactive.")

        return user

    async def issue_tokens(
        self,
        user_id: int,
        role: str,
    ) -> dict[str, str]:

        access_token = create_access_token(
            user_id=user_id,
            role=role
        )
        refresh_token, jti, expires_at = create_refresh_token(
            user_id=user_id,
            role=role
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
        user = await self.authenticate(username, password)

        try:
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
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError(
                "Invalid or expired refresh token."
            ) from exc

        if payload.get("type") != "refresh":
            raise AuthenticationError(
                "Invalid or expired refresh token."
            )

        try:
            user_id = int(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise AuthenticationError(
                "Invalid or expired refresh token."
            ) from exc

        jti = payload.get("jti")
        if not isinstance(jti, str):
            raise AuthenticationError(
                "Invalid or expired refresh token."
            )

        try:
            token_record = await self.refresh_tokens.get_valid_for_update(
                jti=jti,
                user_id=user_id,
                token_hash=hash_refresh_token(raw_refresh_token),
            )

            if token_record is None:
                raise AuthenticationError(
                    "Invalid, expired, or revoked refresh token."
                )

            user = await self.users.get_by_id(user_id)
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

        except Exception:
            await self.db.rollback()
            raise

    async def logout(
        self,
        raw_refresh_token: str,
        current_user_id: int,
    ) -> None:
        try:
            payload = decode_token(raw_refresh_token)
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError(
                "Invalid refresh token."
            ) from exc

        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token.")

        try:
            user_id = int(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise AuthenticationError(
                "Invalid refresh token."
            ) from exc

        if user_id != current_user_id:
            raise AuthenticationError("Invalid refresh token.")

        jti = payload.get("jti")
        if not isinstance(jti, str):
            raise AuthenticationError("Invalid refresh token.")

        try:
            token_record = await self.refresh_tokens.get_valid_for_update(
                jti=jti,
                user_id=user_id,
                token_hash=hash_refresh_token(raw_refresh_token),
            )

            if token_record is None:
                raise AuthenticationError(
                    "Refresh token is invalid, expired, or revoked."
                )

            await self.refresh_tokens.revoke(token_record)
            await self.db.commit()

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

        user = await self.users.get_by_id(user_id)

        if user is None or not user.is_active:
            raise AuthenticationError(
                "Invalid authentication token."
            )

        return user