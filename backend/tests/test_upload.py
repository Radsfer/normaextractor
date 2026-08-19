"""Testes de upload (REQ-FUNC-001)."""
import io

from app.config import get_settings


def _bytes(size: int) -> bytes:
    # conteúdo ASCII suficiente para passar no tamanho mínimo
    return (b"x" * size) if size < 2000 else (b"NormaExtractor test file\n" * (size // 22 + 1))[:size]


def test_upload_pdf(client, auth_headers, fake_queue):
    data = _bytes(2048)
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("norma.pdf", data, "application/pdf")},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "queued"
    assert body["document_id"]
    assert len(fake_queue.enqueued) == 1


def test_upload_docx(client, auth_headers, fake_queue):
    resp = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "norma.docx",
                _bytes(2048),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text


def test_upload_txt(client, auth_headers, fake_queue):
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("norma.txt", _bytes(2048), "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text


def test_upload_png_rejected(client, auth_headers):
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("img.png", _bytes(2048), "image/png")},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Formato de arquivo não suportado"


def test_upload_too_large(client, auth_headers):
    settings = get_settings()
    big = b"a" * (settings.MAX_UPLOAD_MB * 1024 * 1024 + 1)
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("big.pdf", big, "application/pdf")},
        headers=auth_headers,
    )
    assert resp.status_code == 413
    assert "20 MB" in resp.json()["detail"]


def test_upload_empty(client, auth_headers):
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("vazio.txt", b"", "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Arquivo vazio"


def test_upload_executable_rejected(client, auth_headers):
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("malware.exe", _bytes(2048), "application/x-msdownload")},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_upload_requires_auth(client):
    resp = client.post(
        "/api/v1/documents/upload",
        files={"file": ("norma.pdf", _bytes(2048), "application/pdf")},
    )
    assert resp.status_code == 401
