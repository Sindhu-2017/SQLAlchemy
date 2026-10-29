import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core import logging_config
from app.api.routers.income_router import router as income_router
from app.api.routers.expense_router import router as expense_router
from app.api.routers.auth_router import router as auth_router


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Income Management API",
    description="Income & Expenses - SQLAlchemy Relationships and Joins",
    version="1.0.0",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)

    except Exception:
        logger.exception(
            "Unhandled exception for %s %s",
            request.method,
            request.url.path,
        )

        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )

    duration = time.perf_counter() - start_time

    message = (
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Duration: {duration:.3f} seconds"
    )

    if response.status_code >= 500:
        logger.error(message)
    elif response.status_code >= 400:
        logger.warning(message)
    else:
        logger.info(message)

    return response


app.include_router(auth_router)
app.include_router(income_router)
app.include_router(expense_router)


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Income and Expense API is running"}
