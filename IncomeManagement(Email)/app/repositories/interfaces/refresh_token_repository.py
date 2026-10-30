from abc import ABC, abstractmethod

from app.models.refresh_token import RefreshToken

class RefreshTokenRepositoryInterface(ABC):

    @abstractmethod
    async def get_valid(
        self,
        jti: str,
        user_id: int,
        token_hash: str,
    ) -> RefreshToken | None:
        ...

    @abstractmethod
    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        ...

    @abstractmethod
    async def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> None:
        ...