"""Ingestão de arquivos: validação de formato/tamanho, SHA-256 e persistência."""
import hashlib
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import Settings

ALLOWED_TYPES: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
}

EXECUTABLE_MIMES = {
    "application/x-executable",
    "application/x-msdownload",
    "application/x-msdos-program",
    "application/x-dosexec",
    "application/x-sh",
    "application/x-elf",
    "application/x-mach-binary",
}


class IngestionError(HTTPException):
    pass


def validate_upload(filename: str | None, mime_type: str | None, size: int, settings: Settings) -> str:
    """Valida extensão + MIME + tamanho. Retorna a extensão normalizada."""
    ext = Path(filename or "").suffix.lower()
    mime = (mime_type or "").split(";")[0].strip().lower()

    if mime in EXECUTABLE_MIMES:
        raise IngestionError(status.HTTP_400_BAD_REQUEST, "Formato de arquivo não suportado")
    if ext not in ALLOWED_TYPES or mime != ALLOWED_TYPES[ext]:
        raise IngestionError(status.HTTP_400_BAD_REQUEST, "Formato de arquivo não suportado")
    if size == 0:
        raise IngestionError(status.HTTP_400_BAD_REQUEST, "Arquivo vazio")
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if size > max_bytes:
        raise IngestionError(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            "Tamanho do arquivo excede o limite de 20 MB",
        )
    if size < settings.MIN_UPLOAD_BYTES:
        raise IngestionError(status.HTTP_400_BAD_REQUEST, "Arquivo menor que o mínimo de 1 KB")
    return ext


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def read_and_save_upload(file: UploadFile, settings: Settings) -> tuple[bytes, str, Path]:
    """Lê o upload, valida e salva em disco. Retorna (bytes, extensão, caminho)."""
    data = await file.read()
    ext = validate_upload(file.filename, file.content_type, len(data), settings)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    path = settings.upload_dir / f"{uuid.uuid4()}{ext}"
    path.write_bytes(data)
    return data, ext, path
