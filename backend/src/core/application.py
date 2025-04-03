from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from src.articles.router import router as articles_router
from src.core.lifetime import (
    register_shutdown_event,
    register_startup_event,
)
from src.embeddings.router import router as embeddings_router


def get_app() -> FastAPI:
    OPENAPI_URL = "/openapi.json"

    app = FastAPI(
        title="deadlock",
        root_path="/api",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=OPENAPI_URL,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    register_startup_event(app)
    register_shutdown_event(app)

    app.include_router(articles_router)
    app.include_router(embeddings_router)

    return app
