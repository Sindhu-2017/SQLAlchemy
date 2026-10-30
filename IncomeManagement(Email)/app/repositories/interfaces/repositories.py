from abc import ABC, abstractmethod
from decimal import Decimal
from app.models.income import Income
from app.models.expense import Expense

# income
class IncomeRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self,page: int,page_size: int,income_name: str | None = None) -> tuple[list[Income], int]:
        pass

    @abstractmethod
    def get_by_id(self, income_id: int) -> Income | None:
        pass

    @abstractmethod
    def create(self, income: Income) -> Income:
        pass

    @abstractmethod
    def update(self, income: Income) -> Income:
        pass

    @abstractmethod
    def delete(self, income: Income) -> None:
        pass

    @abstractmethod
    def get_income_summary(self,min_expense: Decimal | None = None) -> list[dict]:
        pass

# expense
class ExpenseRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, expense_id: int) -> Expense | None:
        pass

    @abstractmethod
    def get_by_income_id(self, income_id: int) -> list[Expense]:
        pass

    @abstractmethod
    def get_total_by_income_id(self, income_id: int):
        pass

    @abstractmethod
    def create(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    def update(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    def delete(self, expense: Expense) -> None:
        pass

    @abstractmethod
    def get_income_expenses_inner_join(self):
        pass

    @abstractmethod
    def get_income_expenses_outer_join(self):
        pass