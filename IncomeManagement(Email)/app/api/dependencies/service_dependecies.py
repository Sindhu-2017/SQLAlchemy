from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.repositories.implementations.expense_repository import (
    ExpenseRepository,
)
from app.repositories.implementations.income_repository import (
    IncomeRepository,
)
from app.repositories.implementations.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.implementations.user_repository import (
    UserRepository,
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailSender
from app.services.expense_service import ExpenseService
from app.services.income_service import IncomeService


async def get_income_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IncomeService:
    return IncomeService(
        db=db,
        income_repository=IncomeRepository(db),
        expense_repository=ExpenseRepository(db),
        email_sender=EmailSender()
    )


async def get_expense_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExpenseService:
    return ExpenseService(
        db=db,
        income_repository=IncomeRepository(db),
        expense_repository=ExpenseRepository(db),
    )


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    return AuthService(
        db=db,
        user_repository=UserRepository(db),
        refresh_token_repository=RefreshTokenRepository(db),
    )