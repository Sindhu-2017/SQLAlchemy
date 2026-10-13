from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.connection import engine
from routers.income_router import router as income_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
    yield
    engine.dispose()


app = FastAPI(
    title="Income Management API",
    description=(
        "Income management using FastAPI, "
        "SQLAlchemy ORM, Pydantic, and PostgreSQL."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(income_router)


@app.get("/", tags=["Root"])
def home():
    return {
        "message": "Income Management API is running",
        "documentation": "/docs",
    }
