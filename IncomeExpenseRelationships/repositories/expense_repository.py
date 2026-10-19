from sqlalchemy.orm import Session
from models.expense import Expense

class ExpenseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.flush()
        self.db.refresh(expense)
        return expense
