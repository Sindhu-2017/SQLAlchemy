from sqlalchemy.orm import Session
from decimal import Decimal

from app.exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError
)
from app.models.income_expense import Income
from app.schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomePatch
)

from app.repositories.interfaces.repositories import (
    IncomeRepositoryInterface,
    ExpenseRepositoryInterface
)
class IncomeService:
    def __init__(
            self,db:Session,
            repository:IncomeRepositoryInterface,
            expense_repository:ExpenseRepositoryInterface
    ):
        self.repository = repository
        self.expense_repository = expense_repository
        self.db=db

    async def get_incomes(self,page: int,page_size: int,income_name: str | None = None) -> dict:
        records, total = await self.repository.get_all(
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


    async def get_income(self, income_id: int) -> Income:
        income =await self.repository.get_by_id(income_id)
        if income is None:
            raise IncomeNotFoundError(income_id)
        return income

    async def calculate_income(self,amount: Decimal,tax_percentage: Decimal,expense_amount: Decimal) -> tuple[Decimal, Decimal, Decimal]:
        tax_amount = amount * tax_percentage / 100
        net_income = amount - tax_amount
        cash_in_hand = net_income - expense_amount

        if expense_amount < 0 or cash_in_hand < 0:
            raise InvalidIncomeOperationError("Expenses cannot exceed net income." )
        return tax_amount, net_income, cash_in_hand

    async def create_income(self, data: IncomeCreate) -> Income:
        tax_amount, net_income, cash_in_hand = (
            await self.calculate_income(data.amount,data.tax_percentage,data.expense_amount)
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
            await self.repository.create(income)
            await self.db.commit()
            await self.db.refresh(income)
            return income
        except Exception:
            await self.db.rollback()
            raise

    async def update_income(self,income_id: int,data: IncomeUpdate) -> Income:
        income = await self.get_income(income_id)
        tax_amount, net_income, cash_in_hand = (
            await self.calculate_income(data.amount,data.tax_percentage,data.expense_amount)
        )
        changes = data.model_dump()
        changes["tax_amount"] = tax_amount
        changes["net_income"] = net_income
        changes["cash_in_hand"] = cash_in_hand

        try:
            for field, value in changes.items():
                setattr(income, field, value)
            await self.repository.update(income)
            await self.db.commit()
            await self.db.refresh(income)
            return income
        except Exception:
            await self.db.rollback()
            raise

    async def patch_income(self,income_id: int, data: IncomePatch) -> Income:
        income = await self.get_income(income_id)
        changes = data.model_dump(exclude_unset=True)
        if not changes:
            raise InvalidIncomeOperationError("Provide at least one field to update.")
        
        for field, value in changes.items():
            if value is None and field != "description":
                raise InvalidIncomeOperationError(f"{field} cannot be null.")

        amount =changes.get("amount", income.amount)
        tax_percentage =changes.get("tax_percentage",income.tax_percentage)
        expense_amount =changes.get("expense_amount",income.expense_amount)
        tax_amount, net_income, cash_in_hand = (
            await self.calculate_income(amount,tax_percentage,expense_amount)
        )
        changes["tax_amount"] = tax_amount
        changes["net_income"] = net_income
        changes["cash_in_hand"] = cash_in_hand

        try:
            for field, value in changes.items():
                setattr(income, field, value)

            await self.repository.update(income)
            await self.db.commit()
            await self.db.refresh(income)
            return income
        except Exception:
            await self.db.rollback()
            raise

    async def delete_income(self, income_id: int) -> dict:
        income =await self.get_income(income_id)
        try:
            await self.repository.delete(income)
            await self.db.commit()      
            return {
                "message" : "Income data deleted successfully"
            }      
        except Exception:
            await self.db.rollback()
            raise

    async def get_income_expenses_inner_join(self) -> list[dict]:
        rows =await self.expense_repository.get_income_expenses_inner_join()
        incomes = {}
        for income, expense in rows:
            if income.income_id not in incomes:
                incomes[income.income_id] = {
                    "income_id": income.income_id,
                    "source": income.source,
                    "amount": income.amount,
                    "expense_amount": income.expense_amount,
                    "cash_in_hand": income.cash_in_hand,
                    "expenses": []
                }
            incomes[income.income_id]["expenses"].append({
                "expense_id": expense.expense_id,
                "expense_name": expense.expense_name,
                "amount": expense.amount,
                "description": expense.description
            })

        return list(incomes.values())


    async def get_income_summary(self,min_expense: Decimal | None = None) -> list[dict]:
        return await self.repository.get_income_summary(min_expense)

    