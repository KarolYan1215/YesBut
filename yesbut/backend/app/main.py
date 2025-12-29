"""
FastAPI Application Entry Point

Main application factory for the YesBut backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.sessions import router as sessions_router
from .api.v1.nodes import router as nodes_router
from .api.v1.edges import router as edges_router
from .api.v1.branches import router as branches_router
from .api.v1.graph import router as graph_router
from .config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Multi-Agent Collaborative Brainstorming System",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(nodes_router, prefix="/api/v1")
    app.include_router(edges_router, prefix="/api/v1")
    app.include_router(branches_router, prefix="/api/v1")
    app.include_router(graph_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"message": "YesBut API", "version": settings.app_version}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
