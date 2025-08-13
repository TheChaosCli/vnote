import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from .routers import auth, notes, tags, folders, health, attachments, sync, graph, search, repos, admin, blocks
from .middleware import RateLimitMiddleware, BodySizeLimitMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="VNote API", version="0.1.0")

    # CORS
    origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
    origin_list = [o.strip() for o in origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # GZip and basic protections
    app.add_middleware(GZipMiddleware, minimum_size=500)
    # Read limits from env
    try:
        rate = int(os.getenv("RATE_LIMIT_PER_MIN", "120"))
    except ValueError:
        rate = 120
    try:
        max_body = int(os.getenv("MAX_BODY_BYTES", str(10 * 1024 * 1024)))
    except ValueError:
        max_body = 10 * 1024 * 1024
    app.add_middleware(RateLimitMiddleware, max_per_minute=rate)
    app.add_middleware(BodySizeLimitMiddleware, max_body_bytes=max_body)

    # Routers
    app.include_router(health.router, tags=["admin"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(notes.router, prefix="/notes", tags=["notes"])
    app.include_router(tags.router, prefix="/tags", tags=["tags"])
    app.include_router(folders.router, prefix="/folders", tags=["folders"])
    app.include_router(attachments.router, prefix="/attachments", tags=["attachments"])
    app.include_router(sync.router, prefix="/sync", tags=["sync"])
    app.include_router(graph.router, prefix="/graph", tags=["graph"])
    app.include_router(search.router, prefix="/search", tags=["search"])
    app.include_router(repos.router, prefix="/repos", tags=["repos"])
    app.include_router(admin.router, prefix="/admin", tags=["admin"])
    app.include_router(blocks.router, tags=["blocks"])  # mixed prefixes

    return app


app = create_app()
