from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.dependency import get_db
from schemas.expense import ExpenseCreate, ExpenseResponse
from services.expense_service import ExpenseService

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])
Db = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(data: ExpenseCreate, db: Db):
    try:
        return ExpenseService(db).create(data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
