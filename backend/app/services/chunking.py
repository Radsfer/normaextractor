"""Segmentação em chunks: <=512 tokens, overlap de 50, cortes em limites de
parágrafo/frase (REQ-FUNC-003).

O tokenizador é injetável: em produção usa-se `llm.tokenize()` do SLM; em
testes (ou sem modelo carregado) usa-se `ApproxTokenizer` (~0,75 palavra/token).
"""
import logging
import math
import re
from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol

logger = logging.getLogger(__name__)

WORDS_PER_TOKEN = 0.75  # aproximação: 1 token ≈ 0,75 palavra

_sentence_split_re = re.compile(r"(?<=[.!?])\s+")
_paragraph_split_re = re.compile(r"\n\s*\n")


class Tokenizer(Protocol):
    def count(self, text: str) -> int: ...


class ApproxTokenizer:
    """Tokenizador aproximado baseado em contagem de palavras (~0,75 palavra/token)."""

    def count(self, text: str) -> int:
        words = len(text.split())
        return max(1, math.ceil(words / WORDS_PER_TOKEN)) if words else 0


class CallableTokenizer:
    """Adapta um callable count(text) -> int ao protocolo Tokenizer."""

    def __init__(self, fn: Callable[[str], int]):
        self._fn = fn

    def count(self, text: str) -> int:
        return self._fn(text)


@dataclass
class ChunkSpec:
    order: int
    text: str  # conteúdo "core" do chunk (sem overlap)
    page_start: Optional[int]
    page_end: Optional[int]
    token_count: int
    overlap_prefix: str = ""  # últimos <=overlap tokens do chunk anterior


@dataclass
class _Sentence:
    text: str
    page: Optional[int]
    tokens: int


def split_sentences(text: str, page: Optional[int], tokenizer: Tokenizer) -> list[_Sentence]:
    """Divide em parágrafos e depois em sentenças, preservando a ordem."""
    sentences: list[_Sentence] = []
    for paragraph in _paragraph_split_re.split(text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for s in _sentence_split_re.split(paragraph):
            s = s.strip()
            if s:
                sentences.append(_Sentence(s, page, tokenizer.count(s)))
    return sentences


def _split_long_sentence(sentence: _Sentence, max_tokens: int, tokenizer: Tokenizer) -> list[_Sentence]:
    """Fallback: sentença maior que max_tokens é dividida por palavras.

    O corte em limite de frase é sempre preferido; este caminho só é usado
    quando uma única sentença excede o tamanho máximo do chunk.
    """
    words = sentence.text.split()
    words_per_chunk = max(1, int(max_tokens * WORDS_PER_TOKEN))
    parts = []
    for i in range(0, len(words), words_per_chunk):
        piece = " ".join(words[i : i + words_per_chunk])
        parts.append(_Sentence(piece, sentence.page, tokenizer.count(piece)))
    logger.warning("Sentença com %d tokens dividida em %d partes", sentence.tokens, len(parts))
    return parts


def chunk_pages(
    pages: list[tuple[Optional[int], str]],
    tokenizer: Tokenizer | None = None,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[ChunkSpec]:
    """Segmenta páginas em chunks.

    - Cada chunk tem no máximo `max_tokens` tokens.
    - Cortes somente em limites de parágrafo/sentença (fallback por palavra).
    - `overlap_prefix` carrega os últimos <=overlap_tokens do chunk anterior.
    - Concatenação dos `text` (sem overlap) reproduz o texto normalizado.
    - Texto com <= max_tokens gera exatamente 1 chunk, sem overlap.
    """
    tokenizer = tokenizer or ApproxTokenizer()
    sentences: list[_Sentence] = []
    for page, text in pages:
        sentences.extend(split_sentences(text, page, tokenizer))

    if not sentences:
        return []

    total_tokens = sum(s.tokens for s in sentences)
    if total_tokens <= max_tokens:
        full = " ".join(s.text for s in sentences)
        pages_seen = [s.page for s in sentences if s.page is not None]
        return [
            ChunkSpec(
                order=0,
                text=full,
                page_start=min(pages_seen) if pages_seen else None,
                page_end=max(pages_seen) if pages_seen else None,
                token_count=tokenizer.count(full),
            )
        ]

    chunks: list[ChunkSpec] = []
    current: list[_Sentence] = []
    current_tokens = 0

    def flush() -> None:
        nonlocal current, current_tokens
        if not current:
            return
        text = " ".join(s.text for s in current)
        pages_seen = [s.page for s in current if s.page is not None]
        prefix = ""
        if chunks and overlap_tokens > 0:
            prev_words = chunks[-1].text.split()
            prefix_words = math.ceil(overlap_tokens * WORDS_PER_TOKEN)
            prefix = " ".join(prev_words[-prefix_words:]) if prev_words else ""
        chunks.append(
            ChunkSpec(
                order=len(chunks),
                text=text,
                page_start=min(pages_seen) if pages_seen else None,
                page_end=max(pages_seen) if pages_seen else None,
                token_count=tokenizer.count(text),
                overlap_prefix=prefix,
            )
        )
        current = []
        current_tokens = 0

    for sentence in sentences:
        parts = [sentence] if sentence.tokens <= max_tokens else _split_long_sentence(sentence, max_tokens, tokenizer)
        for part in parts:
            if current and current_tokens + part.tokens > max_tokens:
                flush()
            current.append(part)
            current_tokens += part.tokens
    flush()
    return chunks


def chunk_text(
    text: str,
    tokenizer: Tokenizer | None = None,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> list[ChunkSpec]:
    """Atalho para textos sem informação de página."""
    return chunk_pages([(None, text)], tokenizer, max_tokens, overlap_tokens)
