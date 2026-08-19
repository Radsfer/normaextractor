"""Testes de autenticação, senhas e health check (REQ-FUNC-011, REQ-SEC)."""
import os

import bcrypt
import pytest
from jose import jwt

from app.config import get_settings
from app.database import SessionLocal
from app.models import User
from app.security import (
    PasswordPolicyError,
    hash_password,
    validate_password_strength,
    verify_password,
)


def test_health_public(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "model_loaded" in body


def test_login_ok(client, auth_headers):
    assert auth_headers["Authorization"].startswith("Bearer ")


def test_login_invalid_password(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": os.environ["ADMIN_EMAIL"], "password": "Wrong@Pass1"},
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "naoexiste@test.com", "password": "Whatever@123"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Credenciais inválidas"


def test_protected_route_without_token(client):
    resp = client.get("/api/v1/documents")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Autenticação necessária"


def test_protected_route_expired_token(client):
    settings = get_settings()
    db = SessionLocal()
    user = db.query(User).first()
    db.close()
    now = 1700000000
    expired = jwt.encode(
        {"sub": user.id, "email": user.email, "iat": now - 7200, "exp": now - 3600},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    resp = client.get("/api/v1/documents", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Token expirado"


def test_token_without_exp_401(client):
    settings = get_settings()
    db = SessionLocal()
    user = db.query(User).first()
    db.close()
    token = jwt.encode(
        {"sub": user.id, "email": user.email, "iat": 1700000000},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    resp = client.get("/api/v1/documents", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_bcrypt_cost_12():
    h = hash_password("Senha@Forte1")
    assert h.startswith("$2b$12$")
    assert len(h) == 60


def test_reject_bcrypt_cost_below_12():
    weak = bcrypt.hashpw(b"Senha@Forte1", bcrypt.gensalt(rounds=10)).decode()
    assert verify_password("Senha@Forte1", weak) is False


def test_password_strength_validation():
    with pytest.raises(PasswordPolicyError):
        validate_password_strength("curt1A!")
    with pytest.raises(PasswordPolicyError):
        validate_password_strength("semmaiuscula1!")
    with pytest.raises(PasswordPolicyError):
        validate_password_strength("SEMNUMEROabc!")
    with pytest.raises(PasswordPolicyError):
        validate_password_strength("SemEspecial1")
    # válida
    validate_password_strength("Senha@Forte1")
