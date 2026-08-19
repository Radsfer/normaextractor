"""Testes de extração estruturada (REQ-FUNC-006/007)."""
import pytest
from pydantic import ValidationError

from app.schemas import ExtractionSchema
from app.services.extraction import extract_from_chunk


def test_schema_accepts_valid_json():
    s = ExtractionSchema.model_validate(
        {"tipo": "obrigação", "sujeito": "empresa", "acao": "emitir relatório", "prazo": "30 dias"}
    )
    assert s.tipo == "obrigação"
    assert s.sujeito == "empresa"


def test_schema_rejects_missing_sujeito():
    with pytest.raises(ValidationError):
        ExtractionSchema.model_validate({"tipo": "obrigação", "acao": "emitir relatório"})


def test_schema_rejects_invalid_tipo():
    with pytest.raises(ValidationError):
        ExtractionSchema.model_validate({"tipo": "qualquer_coisa", "sujeito": "x", "acao": "y"})


def test_schema_allows_null_fields_for_non_identified():
    s = ExtractionSchema.model_validate(
        {
            "tipo": "não_identificado",
            "sujeito": None,
            "acao": None,
            "prazo": None,
            "base_legal": None,
            "penalidade": None,
        }
    )
    assert s.tipo == "não_identificado"


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def generate(self, prompt, max_tokens=512, temperature=0.1):
        self.calls += 1
        idx = min(self.calls, len(self.responses)) - 1
        return self.responses[idx]


VALID_JSON = '{"tipo": "obrigação", "sujeito": "empresa", "acao": "emitir", "prazo": null, "base_legal": null, "penalidade": null}'


def test_extract_valid_first_attempt():
    llm = FakeLLM([VALID_JSON])
    result = extract_from_chunk(llm, "A empresa deve emitir relatório.")
    assert result.schema is not None
    assert result.schema.tipo == "obrigação"
    assert result.attempts == 1


def test_extract_marks_non_extractable_after_3_failures():
    llm = FakeLLM(["resposta inválida", "ainda inválida", "nada de json"])
    result = extract_from_chunk(llm, "texto qualquer")
    assert result.schema is None
    assert result.attempts == 3
    assert llm.calls == 3


def test_extract_retries_on_validation_failure():
    # 1ª resposta válida em JSON mas sem sujeito -> validação falha; 2ª válida.
    llm = FakeLLM(
        [
            '{"tipo": "obrigação", "acao": "emitir"}',
            VALID_JSON,
        ]
    )
    result = extract_from_chunk(llm, "A empresa deve emitir relatório.")
    assert result.schema is not None
    assert result.attempts == 2
