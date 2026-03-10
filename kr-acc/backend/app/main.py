"""FastAPI application factory for kr-acc."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.bills import router as bills_router
from app.api.graph import router as graph_router
from app.api.parties import router as parties_router
from app.api.politicians import router as politicians_router
from app.api.votes import router as votes_router
from app.config import settings


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

    # API routes
    api_prefix = "/api"
    application.include_router(politicians_router, prefix=api_prefix)
    application.include_router(bills_router, prefix=api_prefix)
    application.include_router(votes_router, prefix=api_prefix)
    application.include_router(graph_router, prefix=api_prefix)
    application.include_router(parties_router, prefix=api_prefix)

    @application.get("/health")
    async def health_check():
        return {"status": "ok"}

    return application


app = create_app()
