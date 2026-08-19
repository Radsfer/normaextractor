"""Testes de métricas (REQ-FUNC-010)."""
from datetime import datetime, timedelta, timezone

import pytest

from app.database import SessionLocal
from app.models import Chunk, Document, Extraction


def _seed():
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    doc = Document(
        filename="norma.pdf",
        mime_type="application/pdf",
        size_bytes=2048,
        sha256="a" * 64,
        status="done",
        uploaded_at=now - timedelta(seconds=10),
        processing_started_at=now - timedelta(seconds=9),
        finished_at=now,
        word_count=100,
        page_count=1,
        file_path="/tmp/norma.pdf",
    )
    db.add(doc)
    db.flush()

    c1 = Chunk(document_id=doc.id, order=0, text="chunk válido", status="valid", attempts=1)
    c2 = Chunk(document_id=doc.id, order=1, text="chunk sem extração", status="non_extractable", attempts=3)
    db.add_all([c1, c2])
    db.flush()

    db.add(
        Extraction(
            chunk_id=c1.id,
            document_id=doc.id,
            tipo="obrigação",
            sujeito="empresa",
            acao="emitir",
            model_version="model",
            schema_version="1.0",
            valid=True,
            attempt=1,
        )
    )
    db.commit()
    db.close()


def test_metrics_calculated(client, auth_headers):
    _seed()
    resp = client.get("/api/v1/metrics", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["documents_count"] == 1
    assert body["chunks_count"] == 2
    assert body["coverage"] == 50.0  # 1 chunk com extração válida de 2
    assert body["consistency"] == 100.0  # 1/1 na 1ª tentativa
    assert body["avg_latency_seconds"] == pytest.approx(10.0, abs=1.0)


def test_metrics_requires_auth(client):
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 401
