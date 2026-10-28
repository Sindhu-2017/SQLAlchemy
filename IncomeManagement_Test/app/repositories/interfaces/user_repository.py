from abc import ABC, abstractmethod
from app.models.user import User

class UserRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(self,user_id: int) -> User | None:
        ...

    @abstractmethod
    async def get_by_username(self,username: str) -> User | None:
        ...

    @abstractmethod
    async def get_by_username_or_email(
        self,
        username: str | None = None,
        email: str | None = None
    ) -> User | None:
        ...

    @abstractmethod
    async def create(self,user: User) -> User:
        ...