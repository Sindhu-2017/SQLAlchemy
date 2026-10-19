from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class ExpenseBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expense_id: int
    expense_date: date
    category: str
    amount: Decimal
    description: str | None

class IncomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    income_id: int
    income_date: date
    source: str
    income_type: str
    amount: Decimal
    tax_percentage: Decimal
    tax_amount: Decimal
    expense_amount: Decimal
    net_income: Decimal
    cash_in_hand: Decimal
    description: str | None
    expenses: list[ExpenseBrief] = []

class IncomeExpenseJoinRow(BaseModel):
    income_id: int
    source: str
    net_income: Decimal
    expense_id: int | None
    category: str | None
    expense_amount: Decimal | None
