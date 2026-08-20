"""RAG: embedding da query -> top-5 no ChromaDB -> prompt -> streaming."""
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContextHit:
    chunk_id: str
    document_id: str
    text: str
    page_start: int | None
    page_end: int | None
    order: int | None
    distance: float


NOT_IN_DOCS_MESSAGE = (
    "A informação solicitada não está nos documentos disponíveis. "
    "Reformule a pergunta ou envie outros documentos."
)

_rag_system_instruction = (
    "Você é um assistente especializado em documentos normativos. "
    "Responda SOMENTE com base no contexto fornecido abaixo, que contém trechos "
    "extraídos dos documentos. Não invente informações que não estejam no contexto. "
    "Quando usar uma informação do contexto, cite o trecho correspondente. "
    "Se a pergunta não puder ser respondida com o contexto, diga explicitamente que "
    "a informação não está nos documentos.\n\n"
)


def build_rag_prompt(query: str, hits: list[ContextHit]) -> str:
    parts = [_rag_system_instruction, "Contexto:\n"]
    for i, hit in enumerate(hits, start=1):
        page = f" [página {hit.page_start}]" if hit.page_start is not None else ""
        parts.append(f"[Trecho {i}{page}]\n{hit.text}\n")
    parts.append(f"\nPergunta:\n{query}\n\nResposta:")
    return "\n".join(parts)


def format_sources(
    hits: list[ContextHit], document_names: dict[str, str], preview_chars: int = 300
) -> list[dict]:
    out = []
    for hit in hits:
        text = hit.text or ""
        out.append(
            {
                "chunk_id": hit.chunk_id,
                "document_id": hit.document_id,
                "document_name": document_names.get(hit.document_id, ""),
                "page": hit.page_start,
                "text_preview": text[:preview_chars] + ("…" if len(text) > preview_chars else ""),
            }
        )
    return out


def search_contexts(
    query: str,
    embedder,
    vectorstore,
    top_k: int = 5,
    document_ids: list[str] | None = None,
    min_similarity: float = 0.5,
) -> list[ContextHit]:
    q_embedding = embedder.encode([query])[0]
    raw = vectorstore.query(q_embedding, top_k=top_k, document_ids=document_ids)
    hits = []
    for r in raw:
        if not r.get("chunk_id"):
            continue
        # ChromaDB (espaço cosseno) retorna distância = 1 - similaridade.
        similarity = 1.0 - float(r.get("distance", 0.0))
        if similarity < min_similarity:
            continue
        hits.append(
            ContextHit(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                text=r.get("text") or "",
                page_start=r.get("page_start"),
                page_end=r.get("page_end"),
                order=r.get("order"),
                distance=r.get("distance", 0.0),
            )
        )
    return hits
