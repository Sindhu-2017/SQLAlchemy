from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.interfaces.refresh_token_repository import (
    RefreshTokenRepositoryInterface,
)

class RefreshTokenRepository(RefreshTokenRepositoryInterface):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_valid_for_update(
        self,
        jti: str,
        user_id: int,
        token_hash: str,
    ) -> RefreshToken | None:
        try:
            statement = (
                select(RefreshToken)
                .where(
                    RefreshToken.jti == jti,
                    RefreshToken.user_id == user_id,
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked.is_(False),
                    RefreshToken.expires_at > datetime.now(timezone.utc),
                )
                .with_for_update()
            )

            result = await self.db.execute(statement)
            return result.scalar_one_or_none()

        except SQLAlchemyError:
            raise

    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        try:
            self.db.add(refresh_token)
            await self.db.flush()
            return refresh_token

        except SQLAlchemyError:
            raise

    async def revoke(self, refresh_token: RefreshToken) -> None:
        try:
            refresh_token.revoked = True
            await self.db.flush()

        except SQLAlchemyError:
            raise
