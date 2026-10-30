import logging
from fastapi import FastAPI
from app.core import logging_config
from app.api.routers.income_router import router as income_router
from app.api.routers.expense_router import router as expense_router
from app.api.routers.auth_router import router as auth_router

from app.middleware.observability import ObservabilityMiddleware
from app.api.routers.health_routes import router as health_router


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Income Management API",
    description="Income & Expenses - SQLAlchemy Relationships and Joins",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(income_router)
app.include_router(expense_router)
app.include_router(health_router)

app.add_middleware(ObservabilityMiddleware)

@app.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Income and Expense API is running"
    }
