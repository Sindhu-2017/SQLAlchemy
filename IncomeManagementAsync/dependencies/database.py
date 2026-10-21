from collections.abc import AsyncGenerator
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession,None,None]:
    async with SessionLocal() as db:
        yield db
