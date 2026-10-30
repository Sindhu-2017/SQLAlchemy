import logging
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import engine
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("/live")
async def liveness_check():
    return {"status": "alive"}


@router.get("/ready")
async def readiness_check():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1") )
        return {
            "status": "ready",
            "checks": {
                "application": "ok",
                "database": "ok",
            },
        }

    except SQLAlchemyError:
        logger.exception("Database readiness check failed")
        raise HTTPException(
            status_code=503,
            detail="Application is not ready"
        )
