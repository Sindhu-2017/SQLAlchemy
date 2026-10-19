from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from models.income import Income
from models.expense import Expense

class IncomeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_with_expenses(self) -> list[Income]:
        stmt = select(Income).options(selectinload(Income.expenses)).order_by(Income.income_id)
        return list(self.db.scalars(stmt).all())

    def get_with_expenses(self, income_id: int) -> Income | None:
        stmt = select(Income).where(Income.income_id == income_id).options(selectinload(Income.expenses))
        return self.db.scalars(stmt).first()

    def get_income_expense_join(self):
        # Explicit SQL JOIN: only matching income/expense rows are returned.
        stmt = (
            select(Income.income_id, Income.source, Income.net_income,
                   Expense.expense_id, Expense.expense_name,
                   Expense.amount.label("expense_amount"))
            .join(Expense, Income.income_id == Expense.income_id)
            .order_by(Income.income_id, Expense.expense_id)
        )
        return self.db.execute(stmt).mappings().all()

    def get_all_income_outer_join(self):
        # LEFT OUTER JOIN also includes incomes that have no expense rows.
        stmt = (
            select(Income.income_id, Income.source, Income.net_income,
                   Expense.expense_id, Expense.category,
                   Expense.amount.label("expense_amount"))
            .outerjoin(Expense, Income.income_id == Expense.income_id)
            .order_by(Income.income_id, Expense.expense_id)
        )
        return self.db.execute(stmt).mappings().all()
