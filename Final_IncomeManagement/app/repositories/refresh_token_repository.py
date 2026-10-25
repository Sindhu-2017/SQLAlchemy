from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

class RefreshTokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_valid(
        self,
        jti: str,
        user_id: int,
        token_hash: str,
    ) -> RefreshToken | None:
        statement = (
            select(RefreshToken)
            .where(
                RefreshToken.jti == jti,
                RefreshToken.user_id == user_id,
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at
                > datetime.now(timezone.utc),
            )
            .with_for_update()
        )
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def create(
        self,
        refresh_token: RefreshToken,
    ) -> RefreshToken:
        
        self.db.add(refresh_token)
        await self.db.flush()
        return refresh_token

    async def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> None:
        refresh_token.revoked = True
        await self.db.flush()