from sqlalchemy.orm import Session
from repositories.income_repository import IncomeRepository
from exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError
)
from models.income_expense import Income

class IncomeService:
    def __init__(self,db:Session):
        self.repository = IncomeRepository(db)

    def get_incomes(self,page: int,page_size: int,income_name: str | None = None) -> dict:
        records, total = self.repository.get_all(
            page=page,
            page_size=page_size,
            income_name=income_name
        )
        offset = (page - 1) * page_size
        total_pages = ((total + page_size - 1) // page_size if total else 0)

        return {
            "records": records,
            "pagination": {
                "total_records": total,
                "page_size": page_size,
                "offset": offset,
                "total_pages": total_pages,
                "page_number": page,
                "has_previous": page > 1 and total > 0,
                "has_next": page < total_pages,
            }
        }


    def get_income(self, income_id: int) -> Income:
        income = self.repository.get_by_id(income_id)
        if income is None:
            raise IncomeNotFoundError(income_id)
        return income

    