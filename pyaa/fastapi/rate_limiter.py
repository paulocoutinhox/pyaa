from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from throttled.fastapi import IPLimiter
from throttled.models import Rate
from throttled.storage.memory import MemoryStorage

PATHS = ("/api/",)


def should_apply_limiter(request: Request) -> bool:
    return request.url.path.startswith(PATHS)


class ConditionalLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, limiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        if not should_apply_limiter(request):
            return await call_next(request)

        return await self.limiter.dispatch(request, call_next)


def setup(app: FastAPI):
    memory = MemoryStorage(cache={})

    ip_limiter = IPLimiter(
        limit=Rate(100, 60),
        storage=memory,
    )

    app.add_middleware(
        ConditionalLimiterMiddleware,
        limiter=ip_limiter,
    )
