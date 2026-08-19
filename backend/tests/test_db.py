"""Testes de banco: FKs e cascata na exclusão de documento."""
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import Chunk, Document, Extraction


def test_delete_document_cascades():
    db = SessionLocal()
    doc = Document(
        filename="norma.pdf",
        mime_type="application/pdf",
        size_bytes=2048,
        sha256="a" * 64,
        status="done",
        uploaded_at=datetime.now(timezone.utc),
        file_path="/tmp/norma.pdf",
    )
    db.add(doc)
    db.flush()
    chunk = Chunk(document_id=doc.id, order=0, text="texto", status="valid", attempts=1)
    db.add(chunk)
    db.flush()
    extraction = Extraction(
        chunk_id=chunk.id,
        document_id=doc.id,
        tipo="obrigação",
        sujeito="s",
        acao="a",
        model_version="m",
        schema_version="1.0",
        valid=True,
        attempt=1,
    )
    db.add(extraction)
    db.commit()

    doc_id = doc.id
    chunk_id = chunk.id
    extr_id = extraction.id

    db.delete(db.get(Document, doc_id))
    db.commit()

    assert db.get(Chunk, chunk_id) is None
    assert db.get(Extraction, extr_id) is None
    db.close()
