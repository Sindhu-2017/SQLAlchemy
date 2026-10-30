from sqlalchemy import select,func
from sqlalchemy.orm import Session,selectinload
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from app.models.income import Income
from app.models.expense import Expense
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.interfaces.repositories import IncomeRepositoryInterface

class IncomeRepository(IncomeRepositoryInterface):
    def __init__(self,db:AsyncSession):
        self.db=db

    # get all incomes
    
    async def get_all(
        self,
        page: int,
        page_size: int,
        income_name: str | None = None,
    ) -> tuple[list[Income], int]:
        try:
            statement = select(Income)

            if income_name:
                statement = statement.where(
                    Income.source.ilike(f"{income_name.strip()}%")
                )

            count_statement = select(func.count()).select_from(
                statement.subquery()
            )
            total = await self.db.scalar(count_statement) or 0

            offset = (page - 1) * page_size
            statement = (
                statement
                .order_by(Income.income_id)
                .offset(offset)
                .limit(page_size)
            )

            result = await self.db.scalars(statement)
            return list(result.all()), total

        except SQLAlchemyError:
            raise


    # post-income data
    async def create(self, income: Income) -> Income:
        try:
            self.db.add(income)
            await self.db.flush()
            await self.db.refresh(income)
            return income

        except SQLAlchemyError:
            raise            
        
    # update income
    async def update(self, income: Income) -> Income:
        try:
            await self.db.flush()
            await self.db.refresh(income)
            return income
        except SQLAlchemyError:
            raise 

    # delete income
    async def delete(self, income: Income) -> None:
        try:
            await self.db.delete(income)
            await self.db.flush()
        except SQLAlchemyError:
            raise 

    # get by income id
    async def get_by_id(self, income_id: int) -> Income | None:
        try:
            statement = (
                select(Income)
                .options(selectinload(Income.expenses))
                .where(Income.income_id == income_id)
            )
            result = await self.db.scalars(statement)
            return result.first()
        
        except SQLAlchemyError:
            raise


    # income summary  based on income type
    
    async def get_income_summary(
        self,
        min_expense: Decimal | None = None,
    ) -> list[dict]:
        try:
            expense_summary = (
                select(
                    Expense.income_id.label("income_id"),
                    func.sum(Expense.amount).label("total_expenses")
                )
                .group_by(Expense.income_id)
                .subquery()
            )

            total_expenses = func.coalesce(
                expense_summary.c.total_expenses, 0
            )

            statement = (
                select(
                    Income.income_type.label("income_type"),
                    func.count(Income.income_id).label("total_records"),
                    func.sum(Income.amount).label("total_income"),
                    func.sum(Income.tax_amount).label("total_tax"),
                    func.sum(total_expenses).label("total_expenses"),
                    func.sum(Income.net_income).label("total_net_income"),
                    func.sum(
                        Income.net_income - total_expenses
                    ).label("remaining_balance"),
                )
                .outerjoin(
                    expense_summary,
                    Income.income_id == expense_summary.c.income_id,
                )
                .group_by(Income.income_type)
            )

            if min_expense is not None:
                statement = statement.having(
                    func.sum(total_expenses) > min_expense
                )

            result = await self.db.execute(
                statement.order_by(Income.income_type)
            )
            rows = result.all()

            return [
                {
                    "income_type": row.income_type,
                    "total_records": row.total_records,
                    "total_income": row.total_income,
                    "total_tax": row.total_tax,
                    "total_expenses": row.total_expenses,
                    "total_net_income": row.total_net_income,
                    "remaining_balance": row.remaining_balance,
                }
                for row in rows
            ]

        except SQLAlchemyError:
            raise
