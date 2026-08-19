"""Aplicação FastAPI: CORS, routers, StaticFiles do frontend e seed do admin."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import FileResponse

from app import deps
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models import User
from app.routers import auth, chat, documents, health, metrics
from app.security import hash_password
from app.services.pipeline import DocumentQueue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent / "static"


class SPAStaticFiles(StaticFiles):
    """Serve arquivos estáticos com fallback para index.html em rotas não-API."""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and not path.startswith("api/"):
                return FileResponse(_STATIC_DIR / "index.html")
            raise


def _seed_admin() -> None:
    """Admin pré-cadastrado via env, idempotente (REQ-FUNC-011)."""
    settings = get_settings()
    if not settings.ADMIN_EMAIL:
        return
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL.lower()).first()
        if existing is not None:
            return
        try:
            password_hash = hash_password(settings.ADMIN_PASSWORD)
        except ValueError as exc:
            logger.error("ADMIN_PASSWORD inválida, admin não criado: %s", exc)
            return
        db.add(
            User(
                email=settings.ADMIN_EMAIL.lower(),
                password_hash=password_hash,
                is_admin=True,
            )
        )
        db.commit()
        logger.info("Admin inicial criado: %s", settings.ADMIN_EMAIL)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.ensure_data_dirs()
    init_db()
    _seed_admin()
    deps.validate_model_at_startup()
    app.state.document_queue = DocumentQueue()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="NormaExtractor", version="1.0.0", lifespan=lifespan)

    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(chat.router)
    app.include_router(metrics.router)

    if _STATIC_DIR.exists():
        app.mount("/", SPAStaticFiles(directory=str(_STATIC_DIR), html=True), name="static")

    return app


app = create_app()
