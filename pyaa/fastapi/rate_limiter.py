from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from throttled.fastapi import IPLimiter, TotalLimiter
from throttled.models import Rate
from throttled.storage.memory import MemoryStorage

IGNORED_PATHS = (
    "/static/",
    "/media/",
)


def should_skip_limiter(request: Request) -> bool:
    path = request.url.path
    return path.startswith(IGNORED_PATHS)


class ConditionalLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, limiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        if should_skip_limiter(request):
            return await call_next(request)

        return await self.limiter.dispatch(request, call_next)


def setup(app: FastAPI):
    memory = MemoryStorage(cache={})

    total_limiter = TotalLimiter(
        limit=Rate(3, 1),
        storage=memory,
    )

    ip_limiter = IPLimiter(
        limit=Rate(5, 1),
        storage=memory,
    )

    app.add_middleware(
        ConditionalLimiterMiddleware,
        limiter=total_limiter,
    )

    app.add_middleware(
        ConditionalLimiterMiddleware,
        limiter=ip_limiter,
    )
