from decimal import Decimal
from sqlalchemy.orm import Session

from models.income import Income
from repositories.income_repository import IncomeRepository
from schemas.income import IncomeCreate, IncomeUpdate, IncomePatch

from exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError,
)
class IncomeService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = IncomeRepository(db)

    @staticmethod
    def calculate_income(amount: Decimal,tax_percentage: Decimal,expense_amount: Decimal) -> tuple[Decimal, Decimal, Decimal]:
        tax_amount = amount * tax_percentage / Decimal("100")
        net_income = amount - tax_amount
        cash_in_hand = net_income - expense_amount
        if expense_amount < 0 or cash_in_hand < 0:
            raise InvalidIncomeOperationError("Expenses cannot exceed net income.")

        return (tax_amount,net_income,cash_in_hand)

    def create_income(self, data: IncomeCreate) -> Income:
        tax_amount, net_income, cash_in_hand = (
            self.calculate_income(data.amount,data.tax_percentage, data.expense_amount)
        )
        income = Income(
            income_date=data.income_date,
            source=data.source,
            income_type=data.income_type,
            amount=data.amount,
            tax_percentage=data.tax_percentage,
            tax_amount=tax_amount,
            expense_amount=Decimal("0"),
            net_income=net_income,
            cash_in_hand=cash_in_hand,
            description=data.description,
        )
        try:
            self.repository.create(income)
            self.db.commit()
            self.db.refresh(income)
            return income
        except Exception:
            self.db.rollback()
            raise

    def get_income(self, income_id: int) -> Income:
        income = self.repository.get_by_id(income_id)
        if income is None:
            raise IncomeNotFoundError(f"Income with ID {income_id} was not found.")
        return income

    def get_incomes(self,page: int,page_size: int,income_name: str | None = None) -> dict:
        records, total = self.repository.get_all(page=page, page_size=page_size,income_name=income_name)

        offset = (page - 1) * page_size
        total_pages = ((total + page_size - 1) // page_size  if total else 0 )
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

    def update_income(self,income_id: int,data: IncomeUpdate) -> Income:
        income = self.get_income(income_id)
        tax_amount, net_income, cash_in_hand = (
            self.calculate_income(data.amount,data.tax_percentage,income.expense_amount)
        )
        changes = data.model_dump()

        changes["tax_amount"] = tax_amount
        changes["net_income"] = net_income
        changes["cash_in_hand"] = cash_in_hand

        try:
            for field, value in changes.items():
                setattr(income, field, value)

            self.repository.update(income)
            self.db.commit()
            self.db.refresh(income)
            return income

        except Exception:
            self.db.rollback()
            raise

    def patch_income(self,income_id: int,data: IncomePatch) -> Income:
        income = self.get_income(income_id)
        changes = data.model_dump(exclude_unset=True)
        if not changes:
            raise InvalidIncomeOperationError("Provide at least one field to update.")
        for field, value in changes.items():
            if value is None and field != "description":
                raise InvalidIncomeOperationError(
                    f"{field} cannot be null."
                )

        amount = changes.get("amount", income.amount)
        tax_percentage = changes.get("tax_percentage",income.tax_percentage)
        tax_amount, net_income, cash_in_hand = (
            self.calculate_income(amount,tax_percentage,income.expense_amount)
        )
        changes["tax_amount"] = tax_amount
        changes["net_income"] = net_income
        changes["cash_in_hand"] = cash_in_hand

        try:
            for field, value in changes.items():
                setattr(income, field, value)
            self.repository.update(income)
            self.db.commit()
            self.db.refresh(income)
            return income

        except Exception:
            self.db.rollback()
            raise


    def delete_income(self, income_id: int) -> None:
        income = self.get_income(income_id)
        try:
            self.repository.delete(income)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise
