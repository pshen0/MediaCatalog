from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.rfc7807_handler import problem


class RFC7807Middleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception:
            return problem(
                status=500,
                title="Internal Server Error",
                detail="An unexpected error occurred.",
            )
