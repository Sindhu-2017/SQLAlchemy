from sqlalchemy import select,func
from sqlalchemy.orm import Session,selectinload
from app.models.income import Income
from app.models.expense import Expense
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.interfaces.repositories import IncomeRepositoryInterface

class IncomeRepository(IncomeRepositoryInterface):
    def __init__(self,db:AsyncSession):
        self.db=db

    # get all incomes
    async def get_all(self,page: int,page_size: int, income_name: str | None = None) -> tuple[list[Income], int]:
        statement = select(Income)
        if income_name:
            statement = statement.where(
                Income.source.ilike(f"{income_name.strip()}%")
            )
        count_statement = select(func.count()).select_from(statement.subquery())

        total = await self.db.scalar(count_statement) or 0
        offset = (page - 1) * page_size

        statement = (statement
                     .order_by(Income.income_id)
                     .offset(offset)
                     .limit(page_size)
                )
        
        result = await self.db.scalars(statement)
        records = list(result.all())
        return records, total

    # post-income data
    async def create(self, income: Income) -> Income:
        self.db.add(income)
        await self.db.flush()
        await self.db.refresh(income)
        return income

    # update income
    async def update(self, income: Income) -> Income:
        await self.db.flush()
        await self.db.refresh(income)
        return income

    # delete income
    async def delete(self, income: Income) -> None:
        await self.db.delete(income)
        await self.db.flush()

    # get by income id
    async def get_by_id(self, income_id: int) -> Income | None:
        statement = (
            select(Income)
            .options(selectinload(Income.expenses))
            .where(Income.income_id == income_id)
        )
        result = await self.db.scalars(statement)
        return result.first()


    # income summary  based on income type
    async def get_income_summary(self,min_expense: Decimal | None = None) -> list[dict]:
        expense_summary = (
            select(
                Expense.income_id.label("income_id"),
                func.sum(Expense.amount).label("total_expenses")
            )
            .group_by(Expense.income_id)
            .subquery()
        )

        total_expenses = func.coalesce(expense_summary.c.total_expenses, 0)

        statement = (
            select(
                Income.income_type.label("income_type"),
                func.count(Income.income_id).label("total_records"),
                func.sum(Income.amount).label("total_income"),
                func.sum(Income.tax_amount).label("total_tax"),
                func.sum(total_expenses).label("total_expenses"),
                func.sum(Income.net_income).label("total_net_income"),
                func.sum(Income.net_income - total_expenses).label("remaining_balance")
            )
            .outerjoin(expense_summary,Income.income_id == expense_summary.c.income_id)
            .group_by(Income.income_type)
        )
        if min_expense is not None:
            statement = statement.having(
                func.sum(total_expenses) > min_expense
            )

        statement = statement.order_by(Income.income_type)
        result = await self.db.execute(statement)
        rows = result.all()

        return [
            {
                "income_type": row.income_type,
                "total_records": row.total_records,
                "total_income": row.total_income,
                "total_tax": row.total_tax,
                "total_expenses": row.total_expenses,
                "total_net_income": row.total_net_income,
                "remaining_balance": row.remaining_balance
            }
            for row in rows
        ]