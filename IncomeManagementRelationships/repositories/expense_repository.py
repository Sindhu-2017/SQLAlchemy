from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from models.income_expense import Income, Expense

class ExpenseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, expense_id: int) -> Expense | None:
        return self.db.get(Expense, expense_id)

    def get_by_id_with_income(self,expense_id: int) -> Expense | None:
        statement = (
            select(Expense)
            .options(selectinload(Expense.income))
            .where(Expense.expense_id == expense_id)
        )
        return self.db.scalars(statement).first()

    def get_by_income_id(self,income_id: int) -> list[Expense]:
        statement = (
            select(Expense)
            .where(Expense.income_id == income_id)
            .order_by(Expense.expense_id)
        )
        return list(self.db.scalars(statement).all())

    def get_total_by_income_id(self, income_id: int):
        statement = (
            select(func.coalesce(func.sum(Expense.amount), 0))
            .where(Expense.income_id == income_id)
        )
        return self.db.scalar(statement)

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.flush()
        self.db.refresh(expense)
        return expense

    def update(self, expense: Expense) -> Expense:
        self.db.flush()
        self.db.refresh(expense)
        return expense

    def delete(self, expense: Expense) -> None:
        self.db.delete(expense)
        self.db.flush()

    # inner join
    def get_income_expenses_inner_join(self):
        statement = (
            select(Income, Expense)
            .join(Expense,Income.income_id == Expense.income_id)
            .order_by(Income.income_id, Expense.expense_id)
        )
        return self.db.execute(statement).all()

    # left outer join
    def get_income_expenses_outer_join(self):
        statement = (
            select(Income, Expense)
            .outerjoin(Expense,Income.income_id == Expense.income_id)
            .order_by(Income.income_id, Expense.expense_id)
        )
        return self.db.execute(statement).all()
