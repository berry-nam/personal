"""FastAPI application factory for kr-acc."""

import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.bills import router as bills_router
from app.api.graph import router as graph_router
from app.api.parties import router as parties_router
from app.api.politicians import router as politicians_router
from app.api.stats import router as stats_router
from app.api.votes import router as votes_router
from app.config import settings


# Simple in-memory rate limiter
_rate_store: dict[str, list[float]] = {}
RATE_LIMIT = 60  # requests per minute (general)
RATE_LIMIT_GRAPH = 10  # requests per minute (graph queries)
RATE_WINDOW = 60.0  # seconds


def _check_rate_limit(client_ip: str, path: str) -> bool:
    """Return True if request is within rate limits."""
    limit = RATE_LIMIT_GRAPH if "/graph" in path else RATE_LIMIT
    key = f"{client_ip}:{'/graph' if '/graph' in path else 'general'}"
    now = time.monotonic()

    timestamps = _rate_store.get(key, [])
    # Prune old timestamps
    timestamps = [t for t in timestamps if now - t < RATE_WINDOW]
    if len(timestamps) >= limit:
        return False
    timestamps.append(now)
    _rate_store[key] = timestamps
    return True


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="kr-acc",
        description="Korean National Assembly Open Graph API",
        version="0.1.0",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_ip, request.url.path):
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )
        response = await call_next(request)
        return response

    # API routes
    api_prefix = "/api"
    application.include_router(politicians_router, prefix=api_prefix)
    application.include_router(bills_router, prefix=api_prefix)
    application.include_router(votes_router, prefix=api_prefix)
    application.include_router(graph_router, prefix=api_prefix)
    application.include_router(parties_router, prefix=api_prefix)
    application.include_router(stats_router, prefix=api_prefix)

    @application.get("/health")
    async def health_check():
        return {"status": "ok"}

    return application


app = create_app()
