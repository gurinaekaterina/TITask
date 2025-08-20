from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import (
    auth as auth_router,
    comments as comments_router,
    files as files_router,
)

app = FastAPI(title="File Validation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(files_router.router)
app.include_router(comments_router.router)


def init_static_files(app: FastAPI) -> None:
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    if frontend_dir.exists():
        app.mount(
            "/frontend",
            StaticFiles(directory=str(frontend_dir), html=True),
            name="frontend",
        )


init_static_files(app)
