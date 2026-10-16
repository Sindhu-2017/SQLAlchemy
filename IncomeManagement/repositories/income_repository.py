from sqlalchemy import func, select,text
from sqlalchemy.orm import Session
from models.income import Income
from decimal import Decimal
from exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError
)

class IncomeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, income: Income) -> Income:
        self.db.add(income)
        self.db.flush()
        self.db.refresh(income)
        return income

    def get_by_id(self, income_id: int) -> Income | None:
        return self.db.get(Income, income_id)
    
    def get_all(self,page: int,page_size: int, income_name: str | None = None) -> tuple[list[Income], int]:
        statement = select(Income)
        if income_name:
            statement = statement.where(Income.source.ilike(f"{income_name.strip()}%"))
        count_statement = select(func.count()).select_from(statement.order_by(None).subquery())

        total = self.db.scalar(count_statement) or 0
        offset = (page - 1) * page_size

        statement = (statement.order_by(Income.income_id).offset(offset).limit(page_size))
        records = list(self.db.scalars(statement).all())
        return records, total

    def update(self, income: Income) -> Income:
        self.db.flush()
        self.db.refresh(income)
        return income

    
    def update_expense_using_procedure(self,income_id: int,expense_amount: Decimal) -> None:
        income = self.get_by_id(income_id)
        if expense_amount > income.net_income:
            raise InvalidIncomeOperationError(
                "Expense amount cannot exceed net income"
            )
        
        self.db.execute(
            text(
                """
                CALL update_income_expense(:income_id,:expense_amount)
                """
            ),
            {"income_id": income_id,"expense_amount": expense_amount},
        )


    def delete(self, income: Income) -> None:
        self.db.delete(income)
        self.db.flush()

    
    def update_file_path(self,income: Income,file_path: str) -> Income:
        income.file_path = file_path
        self.db.flush()
        self.db.refresh(income)
        return income

