"""Schemas Pydantic da API e schema versionado de extração."""
import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SCHEMA_VERSION = "1.0"

TIPOS_NORMA = Literal["obrigação", "proibição", "direito", "permissão", "penalidade", "não_identificado"]


# ---------- Extração estruturada (REQ-FUNC-006/007) ----------


class ExtractionSchema(BaseModel):
    """Schema versionado da extração estruturada de um chunk."""

    model_config = ConfigDict(str_strip_whitespace=True)

    tipo: TIPOS_NORMA
    sujeito: Optional[str] = None
    acao: Optional[str] = None
    prazo: Optional[str] = None
    base_legal: Optional[str] = None
    penalidade: Optional[str] = None

    @field_validator("sujeito", "acao", "prazo", "base_legal", "penalidade", mode="before")
    @classmethod
    def _empty_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @model_validator(mode="after")
    def _check_required(self):
        if self.tipo == "não_identificado":
            return self
        if not self.sujeito or not self.acao:
            raise ValueError("sujeito e acao são obrigatórios quando tipo != 'não_identificado'")
        return self


# ---------- Auth ----------


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class UserOut(BaseModel):
    id: str
    email: str
    is_admin: bool


# ---------- Documentos ----------


class UploadResponse(BaseModel):
    document_id: uuid.UUID
    id: str
    filename: str
    doc_type: str
    status: str = "queued"
    message: str
    word_count: Optional[int] = None
    uploaded_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    doc_type: str
    mime_type: str
    size_bytes: int
    sha256: str
    status: str
    error_message: Optional[str] = None
    uploaded_at: datetime
    processing_started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    chunks_count: int = 0
    extractions_count: int = 0


class ExtractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chunk_id: str
    document_id: str
    tipo: str
    sujeito: Optional[str]
    acao: Optional[str]
    prazo: Optional[str]
    base_legal: Optional[str]
    penalidade: Optional[str]
    extracted_at: datetime
    model_version: str
    schema_version: str
    valid: bool
    attempt: int


# ---------- Chat ----------


class ChatRequest(BaseModel):
    query: str = Field(min_length=5, max_length=500)
    document_ids: Optional[list[uuid.UUID]] = None


class SourceItem(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page: Optional[int] = None
    text_preview: str


# ---------- Métricas ----------


class MetricsResponse(BaseModel):
    coverage: float  # % chunks com extração válida
    consistency: float  # % extrações válidas na 1ª tentativa
    avg_latency_seconds: float  # média upload -> fim do processamento (0 quando não há dados)
    documents_count: int
    chunks_count: int


# ---------- Health ----------


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: Optional[str] = None
    rss_mb: float
    uptime_seconds: float
