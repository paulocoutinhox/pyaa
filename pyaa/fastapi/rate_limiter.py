from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from throttled.fastapi import IPLimiter, TotalLimiter
from throttled.models import Rate
from throttled.storage.memory import MemoryStorage


def setup(app: FastAPI):
    memory = MemoryStorage(cache={})
    total_limiter = TotalLimiter(limit=Rate(3, 1), storage=memory)
    ip_limiter = IPLimiter(limit=Rate(5, 1), storage=memory)

    app.add_middleware(BaseHTTPMiddleware, dispatch=total_limiter.dispatch)
    app.add_middleware(BaseHTTPMiddleware, dispatch=ip_limiter.dispatch)
