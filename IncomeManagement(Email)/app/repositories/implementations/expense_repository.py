from sqlalchemy import select, func,text
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal

from app.models.income import Income
from app.models.expense import Expense
from app.repositories.interfaces.repositories import ExpenseRepositoryInterface


class ExpenseRepository(ExpenseRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    # get by expense id
    async def get_by_id(self, expense_id: int) -> Expense | None:
        try:
            return await self.db.get(Expense, expense_id)
        except SQLAlchemyError:
            raise


    # get by income id
    async def get_by_income_id(self,income_id: int) -> list[Expense]:
        try:
            statement = (
                select(Expense)
                .options(joinedload(Expense.income))
                .where(Expense.income_id == income_id)
                .order_by(Expense.expense_id)
            )
            result = await self.db.scalars(statement)
            return list(result.all())

        except SQLAlchemyError:
            raise

    # total expenses based on income id
    async def get_total_by_income_id(self, income_id: int) -> Decimal:
        try:
            statement = (
                select(func.coalesce(func.sum(Expense.amount), 0))
                .where(Expense.income_id == income_id)
            )
            total = await self.db.scalar(statement)
            return Decimal(str(total or 0))

        except SQLAlchemyError:
            raise

    # creating expense data using stored procedure
    async def create(self, expense: Expense) -> Expense:
        try:
            statement = text("""
                CALL create_expense(
                    :p_income_id,
                    :p_expense_name,
                    :p_amount,
                    :p_payment_method,
                    :p_expense_date,
                    :p_description,
                    :p_expense_id
                )
            """)
            result = await self.db.execute(
                statement,
                {
                    "p_income_id": expense.income_id,
                    "p_expense_name": expense.expense_name,
                    "p_amount": expense.amount,
                    "p_payment_method": expense.payment_method,
                    "p_expense_date": expense.expense_date,
                    "p_description": expense.description,
                    "p_expense_id": None,
                }
            )
            row = result.one()
            expense.expense_id = row[0]
            return expense
        except SQLAlchemyError:
            raise

    # update expense
    async def update(self, expense: Expense) -> Expense:
        try:
            await self.db.flush()
            await self.db.refresh(expense)
            return expense
        except SQLAlchemyError:
            raise


    # delete expense
    async def delete(self, expense: Expense) -> None:
        try:
            await self.db.delete(expense)
            await self.db.flush()

        except SQLAlchemyError:
            raise

    # inner join
    async def get_income_expenses_inner_join(self) -> list:
        try:
            statement = (
                select(Income, Expense)
                .join(Expense, Income.income_id == Expense.income_id)
                .order_by(Income.income_id, Expense.expense_id)
            )
            result = await self.db.execute(statement)
            return result.all()

        except SQLAlchemyError:
            raise
    
    # left outer join
    async def get_income_expenses_outer_join(self) -> list:
        try:
            statement = (
                select(Income, Expense)
                .outerjoin(Expense, Income.income_id == Expense.income_id)
                .order_by(Income.income_id, Expense.expense_id)
            )
            result = await self.db.execute(statement)
            return result.all()

        except SQLAlchemyError:
            raise