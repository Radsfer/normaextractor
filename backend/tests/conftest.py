"""Fixtures pytest: banco SQLite temporário, diretório de dados temporário e
substituição dos singletons (LLM/embedder/chroma) — nenhum modelo é carregado."""
import os
import tempfile

_TMP = tempfile.mkdtemp(prefix="normaextractor_test_")
os.environ["DATA_DIR"] = _TMP
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["ADMIN_EMAIL"] = "admin@test.com"
os.environ["ADMIN_PASSWORD"] = "Admin@1234"
os.environ["MODEL_PATH"] = os.path.join(_TMP, "nonexistent.gguf")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import deps  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_state():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    deps.reset()
    app.dependency_overrides.clear()
    yield
    Base.metadata.drop_all(bind=engine)
    deps.reset()
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": os.environ["ADMIN_EMAIL"], "password": os.environ["ADMIN_PASSWORD"]},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class FakeQueue:
    def __init__(self):
        self.enqueued = []

    def enqueue(self, document_id: str) -> None:
        self.enqueued.append(document_id)


@pytest.fixture
def fake_queue():
    q = FakeQueue()
    app.dependency_overrides[deps.get_queue] = lambda: q
    return q
