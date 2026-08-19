"""Rotas de documentos: upload, listagem, detalhe, exclusão e extrações."""
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_queue
from app.models import Chunk, Document, Extraction, MIME_BY_DOC_TYPE, User
from app.schemas import DocumentOut, ExtractionOut, UploadResponse
from app.security import get_current_user
from app.services.ingestion import read_and_save_upload, sha256_bytes

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


def _document_out(db: Session, doc: Document) -> DocumentOut:
    chunks_count = db.scalar(select(func.count()).select_from(Chunk).where(Chunk.document_id == doc.id)) or 0
    extractions_count = (
        db.scalar(select(func.count()).select_from(Extraction).where(Extraction.document_id == doc.id)) or 0
    )
    out = DocumentOut.model_validate(doc)
    out.chunks_count = chunks_count
    out.extractions_count = extractions_count
    return out


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_200_OK)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    queue=Depends(get_queue),
) -> UploadResponse:
    from app.config import get_settings

    settings = get_settings()
    data, ext, path = await read_and_save_upload(file, settings)

    document = Document(
        filename=file.filename or f"document{ext}",
        mime_type=(file.content_type or "").split(";")[0].strip().lower(),
        size_bytes=len(data),
        sha256=sha256_bytes(data),
        status="queued",
        file_path=str(path),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    queue.enqueue(document.id)
    return UploadResponse(
        document_id=uuid.UUID(document.id),
        id=document.id,
        filename=document.filename,
        doc_type=document.doc_type,
        status="queued",
        message="Documento enfileirado para processamento",
        word_count=None,
        uploaded_at=document.uploaded_at,
    )


@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    status_filter: str | None = Query(default=None, alias="status"),
    doc_type: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
) -> list[DocumentOut]:
    filters = []
    if status_filter:
        filters.append(Document.status == status_filter)
    if doc_type:
        mime = MIME_BY_DOC_TYPE.get(doc_type.upper())
        if mime is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Tipo de documento inválido")
        filters.append(Document.mime_type == mime)
    if date_from is not None:
        filters.append(Document.uploaded_at >= date_from)
    if date_to is not None:
        filters.append(Document.uploaded_at <= date_to)

    docs = db.scalars(
        select(Document).where(*filters).order_by(Document.uploaded_at.desc())
    ).all()
    return [_document_out(db, d) for d in docs]


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> DocumentOut:
    doc = db.get(Document, str(document_id))
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento não encontrado")
    return _document_out(db, doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> None:
    from app import deps

    doc = db.get(Document, str(document_id))
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento não encontrado")

    # Remove do ChromaDB e arquivos em disco (best-effort, DB é fonte da verdade).
    try:
        vs = deps._vectorstore
        if vs is not None:
            vs.delete_document(str(document_id))
    except Exception:  # noqa: BLE001
        pass

    db.delete(doc)  # cascata para chunks/extractions via FK ondelete
    db.commit()

    for path_str in (doc.file_path, doc.text_path):
        if path_str:
            try:
                Path(path_str).unlink(missing_ok=True)
            except Exception:  # noqa: BLE001
                pass


@router.get("/{document_id}/extractions", response_model=list[ExtractionOut])
def list_extractions(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ExtractionOut]:
    doc = db.get(Document, str(document_id))
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento não encontrado")
    rows = db.scalars(
        select(Extraction).where(Extraction.document_id == str(document_id)).order_by(Extraction.extracted_at)
    ).all()
    return [ExtractionOut.model_validate(r) for r in rows]
