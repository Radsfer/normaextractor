"""Autenticação e senhas: bcrypt (custo 12) + JWT HS256 (24h)."""
import re
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User

_bearer = HTTPBearer(auto_error=False)

MIN_BCRYPT_COST = 12
MAX_BCRYPT_PASSWORD_BYTES = 72  # limite do algoritmo bcrypt

_cost_re = re.compile(r"^\$2[aby]\$(\d{2})\$")


class PasswordPolicyError(ValueError):
    pass


def validate_password_strength(password: str) -> None:
    """Mín 8 chars, >=1 maiúscula, 1 minúscula, 1 número, 1 especial (REQ-SEC-001)."""
    if len(password) < 8:
        raise PasswordPolicyError("A senha deve ter no mínimo 8 caracteres")
    if len(password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
        raise PasswordPolicyError("A senha excede o limite de 72 bytes do bcrypt")
    if not re.search(r"[A-Z]", password):
        raise PasswordPolicyError("A senha deve conter ao menos 1 letra maiúscula")
    if not re.search(r"[a-z]", password):
        raise PasswordPolicyError("A senha deve conter ao menos 1 letra minúscula")
    if not re.search(r"[0-9]", password):
        raise PasswordPolicyError("A senha deve conter ao menos 1 número")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise PasswordPolicyError("A senha deve conter ao menos 1 caractere especial")


def hash_password(password: str) -> str:
    """Gera hash bcrypt com custo 12 (formato $2b$12$..., 60 chars)."""
    validate_password_strength(password)
    rounds = max(get_settings().BCRYPT_ROUNDS, MIN_BCRYPT_COST)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=rounds)).decode("utf-8")


def bcrypt_cost(password_hash: str) -> int | None:
    m = _cost_re.match(password_hash or "")
    return int(m.group(1)) if m else None


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica senha; rejeita hashes com custo < 12 (REQ-SEC-002)."""
    cost = bcrypt_cost(password_hash)
    if cost is None or cost < MIN_BCRYPT_COST:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user: User) -> tuple[str, int]:
    """JWT HS256 com claims iat/exp; expiração = 24h. Retorna (token, expires_in_s)."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    claims = {
        "sub": user.id,
        "email": user.email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, settings.JWT_EXPIRE_HOURS * 3600


def decode_access_token(token: str) -> dict:
    """Decodifica e valida o JWT. Lança HTTPException 401 com mensagem adequada."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expirado")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
    if "exp" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido: claim 'exp' ausente")
    if not payload.get("sub"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Dependência que exige JWT válido em todas as rotas protegidas."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Autenticação necessária")
    payload = decode_access_token(credentials.credentials)
    user = db.get(User, payload["sub"])
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido")
    return user
