from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from database.dependency import get_db
from schemas.income import IncomeResponse, IncomeExpenseJoinRow
from services.income_service import IncomeService

router = APIRouter(prefix="/api/income", tags=["Income"])
Db = Annotated[Session, Depends(get_db)]

@router.get("/", response_model=list[IncomeResponse])
def list_income(db: Db):
    return IncomeService(db).all()

@router.get("/join", response_model=list[IncomeExpenseJoinRow])
def income_expense_inner_join(db: Db):
    return IncomeService(db).joined()

@router.get("/left-join", response_model=list[IncomeExpenseJoinRow])
def income_expense_left_join(db: Db):
    return IncomeService(db).outer_joined()

@router.get("/{income_id}", response_model=IncomeResponse)
def get_income(income_id: Annotated[int, Path(gt=0)], db: Db):
    row = IncomeService(db).one(income_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Income not found")
    return row
