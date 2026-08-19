"""Rota de chat RAG com streaming SSE (REQ-FUNC-009/012)."""
import asyncio
import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import deps
from app.database import get_db
from app.models import Document, User
from app.schemas import ChatRequest
from app.security import get_current_user
from app.services.rag import (
    NOT_IN_DOCS_MESSAGE,
    build_rag_prompt,
    format_sources,
    search_contexts,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["chat"])

_SENTINEL = object()


def _sse(event_type: str, payload: dict) -> str:
    return f"data: {json.dumps({**payload, 'type': event_type}, ensure_ascii=False)}\n\n"


async def _chat_stream(
    body: ChatRequest, request: Request, db: Session
) -> AsyncIterator[str]:
    llm = deps.get_llm_optional()
    if llm is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Modelo SLM indisponível")

    try:
        embedder = deps.get_embedder()
        vectorstore = deps.get_vectorstore()
        document_ids = [str(d) for d in body.document_ids] if body.document_ids else None

        hits = search_contexts(
            body.query,
            embedder,
            vectorstore,
            top_k=deps.get_settings().RAG_TOP_K,
            document_ids=document_ids,
        )

        if not hits:
            for token in NOT_IN_DOCS_MESSAGE:
                if await request.is_disconnected():
                    return
                yield _sse("token", {"content": token})
            yield _sse("sources", {"sources": []})
            yield _sse("done", {})
            return

        names = {}
        if hits:
            ids = {h.document_id for h in hits if h.document_id}
            docs = db.scalars(select(Document).where(Document.id.in_(ids))).all()
            names = {d.id: d.filename for d in docs}

        prompt = build_rag_prompt(body.query, hits)
        iterator = iter(llm.generate_stream(prompt))
        while True:
            if await request.is_disconnected():
                return
            try:
                token = await asyncio.to_thread(next, iterator, _SENTINEL)
            except StopIteration:
                break
            if token is _SENTINEL:
                break
            if token:
                yield _sse("token", {"content": token})

        yield _sse("sources", {"sources": format_sources(hits, names)})
        yield _sse("done", {})
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erro no streaming do chat")
        yield _sse("error", {"message": str(exc)})


@router.post("/chat")
async def chat(
    body: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    if deps.get_llm_optional() is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Modelo SLM indisponível")
    return StreamingResponse(
        _chat_stream(body, request, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
