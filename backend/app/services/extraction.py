"""Extração estruturada via SLM local: prompt -> JSON -> validação Pydantic -> retry."""
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional, Protocol

from app.schemas import ExtractionSchema, SCHEMA_VERSION

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

_base_prompt = """Você é um extrator de informações normativas. Analise o trecho abaixo e responda APENAS com um objeto JSON válido (sem comentários, sem markdown).

Regras:
- "tipo" DEVE ser um destes valores: "obrigação", "proibição", "direito", "permissão", "penalidade", "não_identificado".
- "sujeito" e "acao" são OBRIGATÓRIOS quando tipo != "não_identificado".
- "prazo", "base_legal" e "penalidade" são opcionais; use null quando não existirem.
- Se o trecho NÃO contiver conteúdo normativo, responda {{"tipo": "não_identificado", "sujeito": null, "acao": null, "prazo": null, "base_legal": null, "penalidade": null}}.

Trecho:
---
{chunk_text}
---

JSON:"""

_reinforced_prompt = """Sua resposta anterior estava em formato inválido ou não atendeu ao schema.

Você DEVE responder APENAS com um JSON válido, exatamente com estas chaves:
{{"tipo": "...", "sujeito": "...", "acao": "...", "prazo": null, "base_legal": null, "penalidade": null}}

"tipo" DEVE ser um de: "obrigação", "proibição", "direito", "permissão", "penalidade", "não_identificado".
"sujeito" e "acao" são OBRIGATÓRIOS (strings não vazias) quando tipo != "não_identificado".
Se não houver conteúdo normativo, use tipo="não_identificado" com sujeito/acao null.

Trecho:
---
{chunk_text}
---

JSON:"""

_json_re = re.compile(r"\{.*\}", re.DOTALL)


class LLM(Protocol):
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str: ...


@dataclass
class ExtractionResult:
    schema: Optional[ExtractionSchema]
    attempts: int


def _parse_json(text: str) -> Optional[dict]:
    """Extrai o primeiro objeto JSON (balanceado) da saída do modelo."""
    m = _json_re.search(text or "")
    if not m:
        return None
    candidate = m.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # tenta o menor objeto JSON válido mais adiante
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None


def build_prompt(chunk_text: str, reinforced: bool = False) -> str:
    template = _reinforced_prompt if reinforced else _base_prompt
    return template.format(chunk_text=chunk_text)


def extract_from_chunk(llm: LLM, chunk_text: str, max_retries: int = MAX_RETRIES) -> ExtractionResult:
    """Executa extração com até `max_retries` tentativas (REQ-FUNC-006/007).

    - JSON inválido ou falha de validação -> nova tentativa com prompt reforçado.
    - Após `max_retries` falhas -> schema None (chunk "não extraível").
    """
    attempts = 0
    last_error: Optional[str] = None
    for attempt in range(1, max_retries + 1):
        attempts = attempt
        prompt = build_prompt(chunk_text, reinforced=attempt > 1)
        try:
            raw = llm.generate(prompt)
            data = _parse_json(raw)
            if data is None:
                last_error = "JSON não encontrado na saída do modelo"
                continue
            schema = ExtractionSchema.model_validate(data)
            return ExtractionResult(schema=schema, attempts=attempt)
        except Exception as exc:  # noqa: BLE001 — validação/infra do LLM
            last_error = str(exc)
            logger.debug("Tentativa %d de extração falhou: %s", attempt, exc)
    logger.warning("Chunk não extraível após %d tentativas: %s", max_retries, last_error)
    return ExtractionResult(schema=None, attempts=attempts)
