from fastapi import FastAPI
from database.base import Base
from database.connection import engine
# Import models so SQLAlchemy registers both tables with Base.metadata.
from models import income, expense  # noqa: F401
from routers.income_router import router as income_router
from routers.expense_router import router as expense_router

app = FastAPI(title="Income & Expenses - SQLAlchemy Relationships and Joins", version="1.0.0")
Base.metadata.create_all(bind=engine)
app.include_router(income_router)
app.include_router(expense_router)

@app.get("/")
def home():
    return {"message": "Income and Expense API is running"}
