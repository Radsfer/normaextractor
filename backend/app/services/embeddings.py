"""Geração de embeddings (REQ-FUNC-004) e validação dos vetores."""
import math

from app.config import get_settings


class EmbeddingError(Exception):
    pass


def validate_embedding(vector: list[float], dim: int | None = None) -> None:
    dim = dim or get_settings().EMBEDDING_DIM
    if len(vector) != dim:
        raise EmbeddingError(f"Embedding com dimensão {len(vector)}, esperado {dim}")
    if not all(math.isfinite(v) for v in vector):
        raise EmbeddingError("Embedding contém valores não finitos")
    norm = math.sqrt(sum(v * v for v in vector))
    if abs(norm - 1.0) > 1e-3:
        raise EmbeddingError(f"Embedding sem norma L2 unitária: {norm}")


def embed_texts(embedder, texts: list[str]) -> list[list[float]]:
    """Gera e valida embeddings. Texto vazio -> EmbeddingError (chunk marcado com erro)."""
    if any(not t.strip() for t in texts):
        raise EmbeddingError("Chunk vazio não pode ser embedado")
    vectors = embedder.encode(texts)
    for v in vectors:
        validate_embedding(v)
    return vectors
