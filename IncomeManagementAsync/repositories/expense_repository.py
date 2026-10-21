from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models.income_expense import Income, Expense
from interfaces.repositories import ExpenseRepositoryInterface
class ExpenseRepository(ExpenseRepositoryInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, expense_id: int) -> Expense | None:
        return await self.db.get(Expense, expense_id)


    async def get_by_income_id(self,income_id: int) -> list[Expense]:
        statement = (
            select(Expense)
            .options(joinedload(Expense.income))
            .where(Expense.income_id == income_id)
            .order_by(Expense.expense_id)
        )
        result = await self.db.scalars(statement)
        return list(result.all())
    
    async def get_total_by_income_id(self, income_id: int):
        statement = (
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(Expense.income_id == income_id)
        )
        return await self.db.scalar(statement)

    async def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def update(self, expense: Expense) -> Expense:
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def delete(self, expense: Expense) -> None:
        await self.db.delete(expense)
        await self.db.flush()

    # inner join
    async def get_income_expenses_inner_join(self):
        statement = (
            select(Income, Expense)
            .join(Expense,Income.income_id == Expense.income_id)
            .order_by(Income.income_id, Expense.expense_id)
        )
        result = await self.db.execute(statement)
        return result.all()
    
    # left outer join
    async def get_income_expenses_outer_join(self):
        statement = (
            select(Income, Expense)
            .outerjoin(Expense,Income.income_id == Expense.income_id)
            .order_by(Income.income_id, Expense.expense_id)
        )
        result = await self.db.execute(statement)
        return result.all()