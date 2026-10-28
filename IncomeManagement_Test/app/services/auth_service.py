from typing import Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password
)
from app.models.user import User
from app.repositories.interfaces.user_repository import (
    UserRepositoryInterface,
)
from app.schemas.auth import RegisterRequest
from app.exceptions.income_exceptions import (
    AuthenticationError,
    RegistrationConflict,
)


class AuthService:
    def __init__(
        self,
        db: AsyncSession,
        user_repository: UserRepositoryInterface
    ) -> None:
        self.db = db
        self.users = user_repository

    async def register(
        self,
        data: RegisterRequest
    ) -> User:
        existing_user = await self.users.get_by_username_or_email(
            username=data.username,
            email=str(data.email),
        )
        if existing_user is not None:
            if existing_user.username == data.username:
                raise RegistrationConflict("Username is already registered")

            raise RegistrationConflict("Email is already registered")

        user = User(
            username=data.username,
            email=str(data.email),
            hashed_password=hash_password(data.password),
            role="user",
            is_active=True
        )

        try:
            await self.users.create(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        except IntegrityError:
            await self.db.rollback()
            raise RegistrationConflict(
                "Username or email is already registered."
            )

        except Exception:
            await self.db.rollback()
            raise

    async def authenticate(
        self,
        username: str,
        password: str
    ) -> User:
        user = await self.users.get_by_username_or_email(username=username)
        if user is None:
            raise AuthenticationError("Invalid username or password")
        
        if not verify_password(
            password,
            user.hashed_password
        ):
            raise AuthenticationError("Invalid username or password")

        if not user.is_active:
            raise AuthenticationError("This account is inactive")
        return user

    async def login(
        self,
        username: str,
        password: str
    ) -> dict[str, str]:
        user = await self.authenticate(
            username=username,
            password=password
        )
        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    async def get_user_from_token(
        self,
        payload: dict[str, Any]
    ) -> User:
        try:
            user_id = int(payload["sub"])
        except (ValueError, TypeError, KeyError) :
            raise AuthenticationError("Invalid authentication token")

        user = await self.users.get_by_id(user_id)

        if user is None or not user.is_active:
            raise AuthenticationError("Invalid authentication token")
        return user
