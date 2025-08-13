from fastapi import FastAPI
from .routers import auth, notes, tags, folders, health, attachments, sync, graph


def create_app() -> FastAPI:
    app = FastAPI(title="VNote API", version="0.1.0")

    # Routers
    app.include_router(health.router, tags=["admin"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(notes.router, prefix="/notes", tags=["notes"])
    app.include_router(tags.router, prefix="/tags", tags=["tags"])
    app.include_router(folders.router, prefix="/folders", tags=["folders"])
    app.include_router(attachments.router, prefix="/attachments", tags=["attachments"])
    app.include_router(sync.router, prefix="/sync", tags=["sync"])
    app.include_router(graph.router, prefix="/graph", tags=["graph"])

    return app


app = create_app()

