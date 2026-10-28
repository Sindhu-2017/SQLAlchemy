from decimal import Decimal
from datetime import date
from pydantic import BaseModel, ConfigDict, Field

class ExpenseCreate(BaseModel):
    expense_name: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0)
    payment_method: str = Field(min_length=2, max_length=30)
    expense_date: date
    description: str | None = None


class ExpensePatch(BaseModel):
    expense_name: str | None = Field(
        default=None, min_length=2, max_length=100
    )
    amount: Decimal | None = Field(default=None, gt=0)
    payment_method: str | None = Field(
        default=None, min_length=2, max_length=30
    )
    expense_date: date | None = None
    description: str | None = None


class IncomeBasicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    income_id: int
    source: str


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expense_id: int
    income_id: int
    expense_name: str
    amount: Decimal
    payment_method: str
    expense_date: date
    description: str | None = None
    income: IncomeBasicResponse | None = None
    