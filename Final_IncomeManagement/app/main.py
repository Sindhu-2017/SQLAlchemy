from contextlib import asynccontextmanager
from app.database.base import  Base
from app.database.connection import engine 
from app import models

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.income_router import router as income_router
from app.routers.expense_router import router as expense_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title ="Income Management API",
    description = "Income & Expenses - SQLAlchemy Relationships and Joins",
    version = "1.0.0",
    lifespan = lifespan
)


app.include_router(income_router)
app.include_router(expense_router)

@app.get("/")
def home():
    return{
        "message": "Income and Expense API is running"
    }