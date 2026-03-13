"""FastAPI application factory for kr-acc."""

from limits import parse as parse_rate_limit
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.assets import router as assets_router
from app.api.bills import router as bills_router
from app.api.graph import router as graph_router
from app.api.parties import router as parties_router
from app.api.politicians import router as politicians_router
from app.api.stats import router as stats_router
from app.api.votes import router as votes_router
from app.config import settings

# ---------------------------------------------------------------------------
# Rate-limit configuration
# ---------------------------------------------------------------------------

# Path prefixes considered "heavy" — graph queries & aggregate stats.
_HEAVY_PREFIXES = ("/api/graph", "/api/stats")

_GENERAL_RATE = parse_rate_limit("100/minute")
_HEAVY_RATE = parse_rate_limit("30/minute")

_storage = MemoryStorage()
_limiter = MovingWindowRateLimiter(_storage)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply path-aware rate limits per client IP.

    * All endpoints:  100 requests / minute per IP
    * Heavy endpoints: 30 requests / minute per IP (additional, stricter bucket)

    The two buckets are tracked independently.
    """

    async def dispatch(self, request: Request, call_next):  # noqa: ANN201
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        is_heavy = any(path.startswith(p) for p in _HEAVY_PREFIXES)

        # Check the stricter heavy-endpoint limit first so we can bail early.
        if is_heavy and not _limiter.hit(_HEAVY_RATE, "heavy", client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "limit": "30/minute (search/heavy endpoints)",
                },
            )

        # General limit applies to every endpoint.
        if not _limiter.hit(_GENERAL_RATE, "general", client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "limit": "100/minute",
                },
            )

        response = await call_next(request)
        return response


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="kr-acc",
        description="Korean National Assembly Open Graph API",
        version="0.1.0",
    )

    # --- Rate limiting (innermost middleware, runs first) ---
    application.add_middleware(RateLimitMiddleware)

    # --- CORS (outermost middleware, runs before rate limiter) ---
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    api_prefix = "/api"
    application.include_router(politicians_router, prefix=api_prefix)
    application.include_router(bills_router, prefix=api_prefix)
    application.include_router(votes_router, prefix=api_prefix)
    application.include_router(graph_router, prefix=api_prefix)
    application.include_router(parties_router, prefix=api_prefix)
    application.include_router(stats_router, prefix=api_prefix)
    application.include_router(assets_router, prefix=api_prefix)

    @application.get("/health")
    async def health_check():
        return {"status": "ok"}

    @application.get("/api/stats")
    async def platform_stats():
        from app.database import get_session
        from app.services import politician_service

        async for session in get_session():
            return await politician_service.get_platform_stats(session)

    return application


app = create_app()
