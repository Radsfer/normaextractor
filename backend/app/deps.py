"""Singletons lazy: LLM (llama-cpp), embedder (sentence-transformers), ChromaDB.

Todos são substituíveis em testes via FastAPI dependency_overrides ou
deps.set_llm/set_embedder/set_vectorstore + deps.reset().
"""
import logging
import threading
from pathlib import Path

from fastapi import Depends, HTTPException, Request, status

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class ModelValidationError(Exception):
    pass


def validate_model_path(settings: Settings) -> None:
    """Valida o arquivo do modelo: existe, extensão .gguf, 500 MB–3 GB (REQ-MAINT-002)."""
    path = Path(settings.MODEL_PATH)
    if not path.is_file():
        raise ModelValidationError(f"Arquivo do modelo não encontrado: {path}")
    if path.suffix.lower() != ".gguf":
        raise ModelValidationError(f"Extensão inválida (esperado .gguf): {path.name}")
    size_mb = path.stat().st_size / (1024 * 1024)
    if not (settings.MODEL_MIN_MB <= size_mb <= settings.MODEL_MAX_MB):
        raise ModelValidationError(
            f"Tamanho do modelo fora do intervalo "
            f"[{settings.MODEL_MIN_MB}, {settings.MODEL_MAX_MB}] MB: {size_mb:.1f} MB"
        )


class LLMEngine:
    """Wrapper thread-safe do llama-cpp-python (1 inferência por vez)."""

    def __init__(self, settings: Settings):
        from llama_cpp import Llama  # import lazy — pesado e opcional em testes

        self._llm = Llama(
            model_path=settings.MODEL_PATH,
            n_ctx=settings.LLM_CONTEXT_SIZE,
            n_threads=settings.LLM_THREADS,
            verbose=False,
        )
        self._lock = threading.Lock()
        self.model_version = settings.model_version

    def tokenize(self, text: str) -> list[int]:
        with self._lock:
            return self._llm.tokenize(text.encode("utf-8"))

    def count_tokens(self, text: str) -> int:
        return len(self.tokenize(text))

    def count(self, text: str) -> int:
        """Alias compatível com o protocolo Tokenizer do serviço de chunking."""
        return self.count_tokens(text)

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str:
        with self._lock:
            out = self._llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um assistente especializado em documentos normativos. "
                            "Responda de forma objetiva e, quando solicitado, APENAS com JSON válido."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
        return (out["choices"][0]["message"].get("content") or "").strip()

    def generate_stream(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3):
        """Gerador token a token em formato de chat. O lock é mantido durante toda a geração."""
        with self._lock:
            stream = self._llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em documentos normativos.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                if not chunk.get("choices"):
                    continue
                delta = chunk["choices"][0].get("delta") or {}
                token = delta.get("content")
                if token:
                    yield token


class SentenceTransformerEmbedder:
    """Embedder all-MiniLM-L6-v2: 384 dim, float32, norma L2 = 1."""

    def __init__(self, settings: Settings):
        from sentence_transformers import SentenceTransformer  # import lazy

        self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dim = settings.EMBEDDING_DIM

    def encode(self, texts: list[str]) -> list[list[float]]:
        import numpy as np

        vectors = self._model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        ).astype(np.float32)
        return [v.tolist() for v in vectors]


class VectorStore:
    """Wrapper do ChromaDB embedded com distância cosseno."""

    COLLECTION_NAME = "normas"

    def __init__(self, settings: Settings):
        import chromadb  # import lazy

        settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunk_ids, texts, embeddings, metadatas) -> None:
        self._collection.add(
            ids=list(chunk_ids),
            documents=list(texts),
            embeddings=list(embeddings),
            metadatas=list(metadatas),
        )

    def query(self, embedding, top_k: int = 5, document_ids: list[str] | None = None) -> list[dict]:
        where = None
        if document_ids:
            if len(document_ids) == 1:
                where = {"document_id": document_ids[0]}
            else:
                where = {"document_id": {"$in": list(document_ids)}}
        result = self._collection.query(
            query_embeddings=[embedding], n_results=top_k, where=where
        )
        out = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        for cid, doc, meta, dist in zip(ids, docs, metas, dists):
            out.append(
                {
                    "chunk_id": cid,
                    "document_id": meta.get("document_id"),
                    "text": doc,
                    "page_start": meta.get("page_start"),
                    "page_end": meta.get("page_end"),
                    "order": meta.get("order"),
                    "distance": dist,
                }
            )
        return out

    def delete_document(self, document_id: str) -> None:
        self._collection.delete(where={"document_id": document_id})


# ---------- singletons lazy ----------

_lock = threading.Lock()
_llm: LLMEngine | None = None
_llm_failed = False
_embedder = None
_vectorstore = None
_model_valid = False


def _load_llm() -> LLMEngine | None:
    global _llm, _llm_failed
    with _lock:
        if _llm is not None or _llm_failed:
            return _llm
        settings = get_settings()
        try:
            validate_model_path(settings)
            _llm = LLMEngine(settings)
            logger.info("Modelo SLM carregado: %s", settings.MODEL_PATH)
        except Exception as exc:  # noqa: BLE001 — sistema sobe sem modelo
            _llm_failed = True
            logger.error("Falha ao carregar modelo SLM: %s", exc)
        return _llm


def get_llm() -> LLMEngine:
    """Dependência FastAPI: retorna o LLM ou 503 se indisponível."""
    llm = _load_llm()
    if llm is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Modelo SLM indisponível")
    return llm


def get_llm_optional() -> LLMEngine | None:
    return _load_llm()


def get_embedder():
    global _embedder
    with _lock:
        if _embedder is None:
            _embedder = SentenceTransformerEmbedder(get_settings())
        return _embedder


def get_vectorstore() -> VectorStore:
    global _vectorstore
    with _lock:
        if _vectorstore is None:
            _vectorstore = VectorStore(get_settings())
        return _vectorstore


def is_model_loaded() -> bool:
    return _llm is not None


def model_was_validated() -> bool:
    """True se o arquivo do modelo passou na validação de inicialização."""
    return _model_valid


def validate_model_at_startup() -> bool:
    """Chamado no startup: valida o MODEL_PATH e registra erro se inválido."""
    global _model_valid
    settings = get_settings()
    try:
        validate_model_path(settings)
        _model_valid = True
    except ModelValidationError as exc:
        _model_valid = False
        logger.error("Validação do modelo falhou: %s. Sistema subirá sem modelo (503 nas rotas do SLM).", exc)
    return _model_valid


# ---------- ganchos para testes ----------


def set_llm(llm) -> None:
    global _llm, _llm_failed
    _llm = llm
    _llm_failed = llm is None


def set_embedder(embedder) -> None:
    global _embedder
    _embedder = embedder


def set_vectorstore(vs) -> None:
    global _vectorstore
    _vectorstore = vs


def reset() -> None:
    global _llm, _llm_failed, _embedder, _vectorstore, _model_valid
    _llm = None
    _llm_failed = False
    _embedder = None
    _vectorstore = None
    _model_valid = False


def get_queue(request: Request):
    """Fila FIFO de processamento (armazenada em app.state)."""
    return request.app.state.document_queue
