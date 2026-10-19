from sqlalchemy import select,func
from sqlalchemy.orm import Session
from models.income_expense import Income

class IncomeRepository:
    def __init__(self,db:Session):
        self.db=db

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

    def get_by_id(self, income_id: int) -> Income | None:
            return self.db.get(Income, income_id)