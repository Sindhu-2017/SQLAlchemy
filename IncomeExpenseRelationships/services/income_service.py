from sqlalchemy.orm import Session
from repositories.income_repository import IncomeRepository

class IncomeService:
    def __init__(self, db: Session):
        self.repo = IncomeRepository(db)

    def all(self):
        return self.repo.get_all_with_expenses()

    def one(self, income_id: int):
        return self.repo.get_with_expenses(income_id)

    def joined(self):
        return self.repo.get_income_expense_join()

    def outer_joined(self):
        return self.repo.get_all_income_outer_join()
