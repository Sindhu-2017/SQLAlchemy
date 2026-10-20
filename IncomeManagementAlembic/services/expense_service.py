from decimal import Decimal
from sqlalchemy.orm import Session
from models.income_expense import Income, Expense
from repositories.income_repository import IncomeRepository
from repositories.expense_repository import ExpenseRepository
from schemas.expense import ExpenseCreate, ExpensePatch
from exceptions.income_exceptions import (
    IncomeNotFoundError,
    InvalidIncomeOperationError,
)

class ExpenseService:
    def __init__(self, db: Session):
        self.db = db
        self.income_repository = IncomeRepository(db)
        self.expense_repository = ExpenseRepository(db)

    def get_income(self, income_id: int) -> Income:
        income = self.income_repository.get_by_id(income_id)
        if income is None:
            raise IncomeNotFoundError(income_id)
        return income

    def get_expense(self, expense_id: int) -> Expense:
        expense = self.expense_repository.get_by_id(expense_id)
        if expense is None:
            raise InvalidIncomeOperationError(f"Expense with ID {expense_id} was not found.")
        return expense

    def recalculate_income(self, income: Income) -> None:
        total = self.expense_repository.get_total_by_income_id(
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

    def add_expense(self,income_id: int,data: ExpenseCreate) -> dict:
        income = self.get_income(income_id)
        expense = Expense(
            income_id=income_id,
            expense_name=data.expense_name.strip(),
            amount=data.amount,
            description=data.description,
        )

        if not expense.expense_name:
            raise InvalidIncomeOperationError("Expense name cannot be blank.")
        try:
            self.expense_repository.create(expense)
            self.recalculate_income(income)
            self.db.commit()
            self.db.refresh(income)

            return {
                "message": "Expense added successfully",
                "expense_id": expense.expense_id,
                "income_id": income.income_id,
                "expense_amount": income.expense_amount,
                "cash_in_hand": income.cash_in_hand,
            }
        except Exception:
            self.db.rollback()
            raise

    def get_expenses(self, income_id: int) -> dict:
        expenses = self.expense_repository.get_by_income_id(income_id)
        return expenses

    def patch_expense(self,expense_id: int,data: ExpensePatch) -> dict:
        expense = self.get_expense(expense_id)
        income = self.get_income(expense.income_id)
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

            self.expense_repository.update(expense)
            self.recalculate_income(income)
            self.db.commit()
            self.db.refresh(income)

            return {
                "message": "Expense updated successfully",
                "expense_id": expense.expense_id,
                "income_id": income.income_id,
                "expense_amount": income.expense_amount,
                "cash_in_hand": income.cash_in_hand,
            }
        except Exception:
            self.db.rollback()
            raise

    def delete_expense(self, expense_id: int) -> dict:
        expense = self.get_expense(expense_id)
        income = self.get_income(expense.income_id)

        try:
            self.expense_repository.delete(expense)
            self.recalculate_income(income)
            self.db.commit()
            self.db.refresh(income)

            return {
                "message": "Expense deleted successfully",
                "income_id": income.income_id,
                "expense_amount": income.expense_amount,
                "cash_in_hand": income.cash_in_hand,
            }
        except Exception:
            self.db.rollback()
            raise

    def get_income_expenses_outer_join(self) -> list[dict]:
        rows = self.expense_repository.get_income_expenses_outer_join()
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
                    "description": expense.description
                })
        return list(incomes.values())