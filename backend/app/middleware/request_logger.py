import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger("app.middleware.request_logger")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "request_id=%s method=%s path=%s status=%s latency_ms=%s client=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
            request.headers.get("X-Client", "unknown"),
        )
        return response

