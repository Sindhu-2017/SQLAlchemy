from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class ExpenseCreate(BaseModel):
    income_id: int
    expense_name: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    description: str | None = None


class ExpenseUpdate(BaseModel):
    expense_name: str | None = Field(
        default=None, min_length=1, max_length=100
    )
    amount: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    description: str | None = None


class ExpenseResponse(BaseModel):
    expense_id: int
    income_id: int
    expense_name: str
    amount: Decimal
    description: str | None

    model_config = ConfigDict(from_attributes=True)