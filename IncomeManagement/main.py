from fastapi import FastAPI
from routers.income_router import router as income_router

app = FastAPI(
    title="Income Management API",
    description=(
        "Income management using FastAPI, "
        "SQLAlchemy ORM, Pydantic, and PostgreSQL."
    ),
    version="1.0.0"
)

app.include_router(income_router)

@app.get("/")
def home():
    return {
        "message": "Income Management API is running"
    }
