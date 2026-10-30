import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = (request.headers.get("X-Correlation-ID") or str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Unhandled exception | %s %s | Correlation ID: %s",
                request.method,
                request.url.path,
                correlation_id
            )
            response = JSONResponse(status_code=500,content={"detail": "Internal Server Error"})

        duration = time.perf_counter() - start_time
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(round(duration * 1000, 2))
        message = (
            f"{request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f} seconds | "
            f"Correlation ID: {correlation_id}"
        )

        if response.status_code >= 500:
            logger.error(message)

        elif response.status_code >= 400:
            logger.warning(message)
        else:
            logger.info(message)
        return response
