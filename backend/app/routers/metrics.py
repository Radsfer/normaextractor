"""Métricas de cobertura, consistência e latência (REQ-FUNC-010)."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Chunk, Document, Extraction, MIME_BY_DOC_TYPE, User
from app.schemas import MetricsResponse
from app.security import get_current_user

router = APIRouter(prefix="/api/v1", tags=["metrics"])


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    document_id: Optional[uuid.UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    doc_type: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> MetricsResponse:
    # Conjunto de documentos que satisfazem os filtros
    doc_filters = []
    if document_id is not None:
        doc_filters.append(Document.id == str(document_id))
    if date_from is not None:
        doc_filters.append(Document.uploaded_at >= date_from)
    if date_to is not None:
        doc_filters.append(Document.uploaded_at <= date_to)
    if doc_type:
        mime = MIME_BY_DOC_TYPE.get(doc_type.upper())
        if mime is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de documento inválido")
        doc_filters.append(Document.mime_type == mime)
    doc_ids = None
    if doc_filters:
        doc_ids = select(Document.id).where(*doc_filters).scalar_subquery()

    def apply(filters):
        if doc_ids is not None:
            filters = filters + (Chunk.document_id.in_(doc_ids),)
        return filters

    chunks_total = db.scalar(select(func.count()).select_from(Chunk).where(*apply(()))) or 0

    valid_chunks = (
        db.scalar(
            select(func.count())
            .select_from(Chunk)
            .join(Extraction, Extraction.chunk_id == Chunk.id)
            .where(Extraction.valid.is_(True), *apply(()))
        )
        or 0
    )
    coverage = round(valid_chunks / chunks_total * 100, 2) if chunks_total else 0.0

    total_extractions = (
        db.scalar(
            select(func.count())
            .select_from(Extraction)
            .where(Extraction.valid.is_(True), *(() if doc_ids is None else (Extraction.document_id.in_(doc_ids),)))
        )
        or 0
    )
    first_try = (
        db.scalar(
            select(func.count())
            .select_from(Extraction)
            .where(
                Extraction.valid.is_(True),
                Extraction.attempt == 1,
                *(() if doc_ids is None else (Extraction.document_id.in_(doc_ids),)),
            )
        )
        or 0
    )
    consistency = round(first_try / total_extractions * 100, 2) if total_extractions else 0.0

    documents_count = (
        db.scalar(select(func.count()).select_from(Document).where(*doc_filters)) if doc_filters else db.scalar(select(func.count()).select_from(Document))
    ) or 0

    # Latência média upload -> fim do processamento (apenas documentos concluídos)
    latency_filters = [Document.status == "done", Document.finished_at.is_not(None)]
    if doc_filters:
        latency_filters += doc_filters
    rows = db.execute(
        select(Document.uploaded_at, Document.finished_at).where(*latency_filters)
    ).all()
    if rows:
        avg_seconds = sum(
            (finish.astimezone(timezone.utc) - start.astimezone(timezone.utc)).total_seconds()
            for start, finish in rows
        ) / len(rows)
        avg_latency = round(avg_seconds, 3)
    else:
        avg_latency = 0.0

    return MetricsResponse(
        coverage=coverage,
        consistency=consistency,
        avg_latency_seconds=avg_latency,
        documents_count=documents_count,
        chunks_count=chunks_total,
    )
