from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.expense import ExpenseResponse
class IncomeCreate(BaseModel):
    income_date : date
    source :str = Field(min_length =2 ,max_length = 100)
    income_type : str = Field(min_length =2 ,max_length = 100)
    amount :Decimal =Field(gt=0)
    tax_percentage :Decimal =Field(ge=0)
    expense_amount : Decimal =Field(ge =0)
    description : str | None = Field ( default = None , max_length = 255)
    
    @field_validator("source", "income_type")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class IncomeUpdate(IncomeCreate):
    pass


class IncomePatch(BaseModel):
    income_date: date | None = None
    source: str | None = Field(default=None,min_length=2,max_length=100)
    income_type: str | None = Field(default=None,min_length=2,max_length=100)
    amount: Decimal | None = Field(default=None,gt=0)
    tax_percentage: Decimal | None = Field(default=None,ge=0,le=100)
    expense_amount : Decimal |None =Field(default=None,ge =0)
    description: str | None = Field(default=None,max_length=255)

    @field_validator("source", "income_type")
    @classmethod
    def validate_patch_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


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
    description: str | None = None
    expenses :list[ExpenseResponse]

class IncomeActionResponse(BaseModel):
    message: str
    income_id: int

class IncomePagination(BaseModel):
    total_records: int
    page_size: int
    offset: int
    total_pages: int
    page_number: int
    has_previous: bool
    has_next: bool


class IncomePaginatedResponse(BaseModel):
    records: list[IncomeResponse]
    pagination: IncomePagination

