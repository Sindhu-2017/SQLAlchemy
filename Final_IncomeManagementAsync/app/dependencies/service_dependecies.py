from fastapi import Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db

from app.services.income_service import IncomeService
from app.services.expense_service import ExpenseService

from app.repositories.implementations.income_repository import IncomeRepository
from app.repositories.implementations.expense_repository import ExpenseRepository


# dependency function for income service
def get_income_service(db: Session = Depends(get_db)) -> IncomeService:
    return IncomeService(
        db=db,
        repository=IncomeRepository(db),
        expense_repository=ExpenseRepository(db)
    )


# dependency function expense service
def get_expense_service(db: Session = Depends(get_db)) -> ExpenseService:
    return ExpenseService(
        db=db,
        income_repository=IncomeRepository(db),
        expense_repository=ExpenseRepository(db)
    )