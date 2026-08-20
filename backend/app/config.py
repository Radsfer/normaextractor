"""Configuração da aplicação via variáveis de ambiente (pydantic-settings)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Modelo SLM (GGUF)
    MODEL_PATH: str = "./models/model.gguf"
    MODEL_MIN_MB: int = 500
    MODEL_MAX_MB: int = 3000
    LLM_CONTEXT_SIZE: int = 4096
    LLM_THREADS: int = 1
    LLM_MAX_TOKENS: int = 512

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # Autenticação
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    BCRYPT_ROUNDS: int = 12
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "Admin@123"

    # Dados
    DATA_DIR: str = "./data"
    DATABASE_URL: str = ""  # default: sqlite:///<DATA_DIR>/normaextractor.db

    # Upload
    MAX_UPLOAD_MB: int = 20
    MIN_UPLOAD_BYTES: int = 1024  # 1 KB

    # Chunking
    CHUNK_MAX_TOKENS: int = 512
    CHUNK_OVERLAP_TOKENS: int = 50

    # RAG
    RAG_TOP_K: int = 5
    RAG_MIN_SIMILARITY: float = 0.5

    # CORS (mesma origem por padrão — frontend servido pelo próprio FastAPI)
    CORS_ORIGINS: str = ""

    @property
    def data_dir(self) -> Path:
        return Path(self.DATA_DIR)

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def text_dir(self) -> Path:
        return self.data_dir / "texts"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"sqlite:///{self.data_dir / 'normaextractor.db'}"

    @property
    def model_version(self) -> str:
        """Nome do arquivo GGUF sem extensão (usado como model_version)."""
        return Path(self.MODEL_PATH).stem

    @property
    def cors_origin_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return []
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def ensure_data_dirs(self) -> None:
        for d in (self.data_dir, self.upload_dir, self.text_dir, self.chroma_dir):
            d.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
