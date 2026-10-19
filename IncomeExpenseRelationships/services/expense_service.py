from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.income import Income
from models.expense import Expense
from repositories.expense_repository import ExpenseRepository

class ExpenseService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExpenseRepository(db)

    def create(self, data):
        income = self.db.get(Income, data.income_id)
        if income is None:
            raise ValueError(f"Income {data.income_id} does not exist")

        # This demo records an expense row and recalculates totals from all rows.
        expense = Expense(**data.model_dump())
        try:
            self.repo.create(expense)
            self.db.flush()
            total = self.db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.income_id == income.income_id
            ).scalar()
            income.expense_amount = Decimal(str(total))
            income.cash_in_hand = income.net_income - income.expense_amount
            self.db.commit()
            self.db.refresh(expense)
            return expense
        except Exception:
            self.db.rollback()
            raise
