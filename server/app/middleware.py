import time
from collections import deque, defaultdict
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_per_minute: int = 120):
        super().__init__(app)
        self.max = max_per_minute
        self.window = 60.0
        self.buckets: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health",):
            return await call_next(request)
        ident = request.client.host if request.client else "anon"
        now = time.time()
        q = self.buckets[ident]
        # Purge old
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.max:
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        q.append(now)
        return await call_next(request)


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_bytes: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max = max_body_bytes

    async def dispatch(self, request: Request, call_next):
        cl = request.headers.get("content-length")
        if cl is not None and cl.isdigit():
            if int(cl) > self.max:
                return JSONResponse({"detail": "request too large"}, status_code=413)
        return await call_next(request)

