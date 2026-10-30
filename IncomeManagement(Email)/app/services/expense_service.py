from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
import logging
from app.models.income import Income
from app.models.expense import Expense

from app.schemas.expense import ExpenseCreate, ExpensePatch
from app.exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError,
)
from app.repositories.interfaces.repositories import (
    IncomeRepositoryInterface,
    ExpenseRepositoryInterface,
)
class ExpenseService:
    def __init__(
            self, db: Session,
            income_repository:IncomeRepositoryInterface,
            expense_repository:ExpenseRepositoryInterface
    ):
        self.db = db
        self.income_repository = income_repository
        self.expense_repository = expense_repository


    # get income by id
    async def get_income(self, income_id: int) -> Income:
        income =await self.income_repository.get_by_id(income_id)

        if income is None:
            raise IncomeNotFoundError(income_id)
        return income


    # get expense by id
    async def get_expense(self, expense_id: int) -> Expense:
        expense =await self.expense_repository.get_by_id(expense_id)

        if expense is None:
            raise InvalidIncomeOperationError(
                f"Expense with ID {expense_id} was not found."
            )
        return expense


    # recalculating net_income and cash in hand when adding or updating expense
    async def recalculate_income(self, income: Income) -> None:
        total =await self.expense_repository.get_total_by_income_id(
            income.income_id
        )
        total = Decimal(str(total or 0))
        net_income = income.amount - income.tax_amount
        cash_in_hand = net_income - total
        if cash_in_hand < 0:
            raise InvalidIncomeOperationError("Total expenses cannot exceed net income." )

        income.expense_amount = total
        income.net_income = net_income
        income.cash_in_hand = cash_in_hand


    # create expense
    async def add_expense(self,income_id: int,data: ExpenseCreate) -> dict:
        income =await self.get_income(income_id)
        expense = Expense(
            income_id=income_id,
            expense_name=data.expense_name.strip(),
            amount=data.amount,
            payment_method=data.payment_method,
            expense_date=data.expense_date,
            description=data.description
        )

        if not expense.expense_name:
            raise InvalidIncomeOperationError("Expense name cannot be blank.")
        try:
            await self.expense_repository.create(expense)
            await self.recalculate_income(income)
            await self.db.commit()
            expense_id = expense.expense_id
            income_id = income.income_id
            await self.db.refresh(income)

            return {
                "message": "Expense added successfully",
                "expense_id": expense_id,
                "income_id": income_id,
                "expense_amount": income.expense_amount,
                "cash_in_hand": income.cash_in_hand,
            }
        except IntegrityError:
            await self.db.rollback()
            raise InvalidIncomeOperationError(
                "The income operation violates a database constraint."
            )

        except SQLAlchemyError:
            await self.db.rollback()
            raise


    # get all expenses based on income id
    async def get_expenses(self, income_id: int) -> dict:
        expenses =await self.expense_repository.get_by_income_id(income_id)
        return expenses

    # patch expense
    async def patch_expense(self,expense_id: int,data: ExpensePatch) -> dict:
        expense =await self.get_expense(expense_id)
        income =await self.get_income(expense.income_id)
        changes = data.model_dump(exclude_unset=True)

        if not changes:
            raise InvalidIncomeOperationError("Provide at least one field to update.")
        
        if any(
            value is None and field != "description"
            for field, value in changes.items()
        ):
            raise InvalidIncomeOperationError("Only description can be set to null." )

        try:
            for field, value in changes.items():
                setattr(expense, field, value)

            await self.expense_repository.update(expense)
            await self.recalculate_income(income)
            await self.db.commit()
            await self.db.refresh(income)

            return {
                "message": "Expense updated successfully",
                "expense_id": expense.expense_id,
                "income_id": income.income_id,
                "expense_amount": income.expense_amount,
                "cash_in_hand": income.cash_in_hand,
            }
        except IntegrityError:
            await self.db.rollback()
            raise InvalidIncomeOperationError(
                "The income operation violates a database constraint."
            )

        except SQLAlchemyError:
            await self.db.rollback()
            raise

    # delete expense
    async def delete_expense(self, expense_id: int) -> dict:
        expense =await self.get_expense(expense_id)
        income =await self.get_income(expense.income_id)

        try:
            await self.expense_repository.delete(expense)
            await self.recalculate_income(income)
            await self.db.commit()
            await self.db.refresh(income)

            return {
                "message": "Expense deleted successfully",
                "income_id": income.income_id,
                "expense_amount": income.expense_amount,
                "cash_in_hand": income.cash_in_hand,
            }
        except IntegrityError:
            await self.db.rollback()
            raise InvalidIncomeOperationError(
                "The income operation violates a database constraint."
            )

        except SQLAlchemyError:
            await self.db.rollback()
            raise


    # outer join
    async def get_income_expenses_outer_join(self) -> list[dict]:
        rows =await self.expense_repository.get_income_expenses_outer_join()
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

            if expense is not None:
                incomes[income.income_id]["expenses"].append({
                    "expense_id": expense.expense_id,
                    "expense_name": expense.expense_name,
                    "amount": expense.amount,
                    "payment_method": expense.payment_method,
                    "expense_date": expense.expense_date,
                    "description": expense.description
                })
        return list(incomes.values())