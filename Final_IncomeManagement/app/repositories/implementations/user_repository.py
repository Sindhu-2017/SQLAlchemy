from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.interfaces.user_repository import (
    UserRepositoryInterface,
)


class UserRepository(UserRepositoryInterface):

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_username_or_email(
        self,
        username: str | None = None,
        email: str | None = None,
    ) -> User | None:
        conditions = []

        if username is not None:
            conditions.append(User.username == username)

        if email is not None:
            conditions.append(User.email == email)

        if not conditions:
            return None

        result = await self.db.execute(
            select(User).where(or_(*conditions))
        )

        return result.scalars().first()

    async def create(
        self,
        user: User,
    ) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user