from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ExpenseCreate(BaseModel):
    expense_name: str = Field(min_length=2, max_length=100)
    amount: Decimal = Field(gt=0)
    description: str | None = None


class ExpensePatch(BaseModel):
    expense_name: str | None = Field(
        default=None, min_length=2, max_length=100
    )
    amount: Decimal | None = Field(default=None, gt=0)
    description: str | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expense_id: int
    income_id: int
    expense_name: str
    amount: Decimal
    description: str | None = None