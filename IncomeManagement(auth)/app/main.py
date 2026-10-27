from fastapi import FastAPI
from app.api.routers.income_router import router as income_router
from app.api.routers.expense_router import router as expense_router
from app.api.routers.auth_router import router as auth_router


app = FastAPI(
    title="Income Management API",
    description="Income & Expenses - SQLAlchemy Relationships and Joins",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(income_router)
app.include_router(expense_router)


@app.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Income and Expense API is running"
    }