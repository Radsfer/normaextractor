"""Pipeline de processamento assíncrono de documentos (queued -> done|error)."""
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Chunk, Document, Extraction
from app.schemas import SCHEMA_VERSION
from app.services.chunking import ApproxTokenizer, chunk_pages
from app.services.conversion import ConversionError, convert
from app.services.embeddings import EmbeddingError, embed_texts
from app.services.extraction import extract_from_chunk

logger = logging.getLogger(__name__)


@dataclass
class Services:
    llm: Optional[object] = None
    embedder: Optional[object] = None
    vectorstore: Optional[object] = None
    tokenizer: Optional[object] = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def resolve_services() -> Services:
    """Resolve singletons a partir de deps (para produção)."""
    from app import deps

    llm = deps.get_llm_optional()
    return Services(
        llm=llm,
        embedder=deps.get_embedder(),
        vectorstore=deps.get_vectorstore(),
        tokenizer=llm if llm is not None else ApproxTokenizer(),
    )


def _model_version(services: Services) -> str:
    if services.llm is not None and getattr(services.llm, "model_version", None):
        return services.llm.model_version
    return get_settings().model_version


def process_document(document_id: str, services: Services | None = None, db: Session | None = None) -> None:
    """Processa um documento de ponta a ponta. Qualquer erro marca status=erro."""
    services = services or resolve_services()
    own_session = db is None
    session = db or SessionLocal()
    try:
        document = session.get(Document, document_id)
        if document is None:
            return
        document.status = "processing"
        document.processing_started_at = _utcnow()
        document.error_message = None
        session.commit()

        # Conversão
        try:
            converted = convert(Path(document.file_path))
        except ConversionError as exc:
            document.status = "error"
            document.error_message = str(exc)
            document.finished_at = _utcnow()
            session.commit()
            return

        # Persistir .txt extraído + hash do texto
        settings = get_settings()
        settings.text_dir.mkdir(parents=True, exist_ok=True)
        text_path = settings.text_dir / f"{document_id}.txt"
        text_path.write_text(converted.text, encoding="utf-8")
        document.text_path = str(text_path)
        document.word_count = converted.word_count
        document.page_count = converted.page_count
        document.extracted_text_sha256 = converted.sha256
        session.commit()

        # Chunking (usa tokenizer do SLM quando disponível, senão aproximação)
        tokenizer = services.tokenizer or ApproxTokenizer()
        chunks = chunk_pages(
            converted.pages,
            tokenizer=tokenizer,
            max_tokens=settings.CHUNK_MAX_TOKENS,
            overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
        )

        chunk_rows: list[Chunk] = []
        for spec in chunks:
            row = Chunk(
                document_id=document_id,
                order=spec.order,
                page_start=spec.page_start,
                page_end=spec.page_end,
                text=spec.text,
                token_count=spec.token_count,
                status="pending",
                attempts=0,
            )
            session.add(row)
            chunk_rows.append(row)
        session.commit()

        # Embeddings + ChromaDB (chunk vazio/erro => status failed e segue)
        if services.embedder is not None and services.vectorstore is not None:
            ids, texts, metas, embeddings = [], [], [], []
            for row in chunk_rows:
                try:
                    vectors = embed_texts(services.embedder, [row.text])
                except EmbeddingError as exc:
                    row.status = "failed"
                    row.error_message = str(exc)
                    continue
                ids.append(row.id)
                texts.append(row.text)
                metas.append(
                    {
                        "document_id": document_id,
                        "order": row.order,
                        "page_start": row.page_start if row.page_start is not None else 1,
                        "page_end": row.page_end if row.page_end is not None else 1,
                    }
                )
                embeddings.append(vectors[0])
            if ids:
                services.vectorstore.add_chunks(ids, texts, embeddings, metas)
        session.commit()

        # Extração estruturada (por chunk)
        model_version = _model_version(services)
        for row in chunk_rows:
            if row.status == "failed":
                continue
            if services.llm is None:
                row.status = "non_extractable"
                row.error_message = "Modelo SLM indisponível"
                row.attempts = 0
                continue
            result = extract_from_chunk(services.llm, row.text)
            row.attempts = result.attempts
            if result.schema is None:
                row.status = "non_extractable"
            else:
                row.status = "valid"
                session.add(
                    Extraction(
                        chunk_id=row.id,
                        document_id=document_id,
                        tipo=result.schema.tipo,
                        sujeito=result.schema.sujeito,
                        acao=result.schema.acao,
                        prazo=result.schema.prazo,
                        base_legal=result.schema.base_legal,
                        penalidade=result.schema.penalidade,
                        extracted_at=_utcnow(),
                        model_version=model_version,
                        schema_version=SCHEMA_VERSION,
                        valid=True,
                        attempt=result.attempts,
                    )
                )
        session.commit()

        document.status = "done"
        document.finished_at = _utcnow()
        session.commit()
    except Exception as exc:  # noqa: BLE001 — nunca derruba a fila
        logger.exception("Erro ao processar documento %s", document_id)
        session.rollback()
        document = session.get(Document, document_id)
        if document is not None:
            document.status = "error"
            document.error_message = str(exc)
            document.finished_at = _utcnow()
            session.commit()
    finally:
        if own_session:
            session.close()


class DocumentQueue:
    """Fila FIFO em memória: processa 1 documento por vez em thread única."""

    def __init__(self, processor: Callable[[str], None] | None = None):
        self._queue: "queue.Queue[str]" = __import__("queue").Queue()
        self._lock = threading.Lock()
        self._worker: threading.Thread | None = None
        self.processor = processor or (lambda doc_id: process_document(doc_id))

    def enqueue(self, document_id: str) -> None:
        self._queue.put(document_id)
        self._ensure_worker()

    def _ensure_worker(self) -> None:
        with self._lock:
            if self._worker is None or not self._worker.is_alive():
                self._worker = threading.Thread(target=self._run, daemon=True, name="document-queue")
                self._worker.start()

    def _run(self) -> None:
        while True:
            document_id = self._queue.get()
            try:
                self.processor(document_id)
            except Exception:  # noqa: BLE001
                logger.exception("Erro não tratado no processador da fila")
            finally:
                self._queue.task_done()

    @property
    def pending(self) -> int:
        return self._queue.qsize()
