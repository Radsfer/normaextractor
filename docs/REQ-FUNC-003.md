# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-003` |
| **Nome** | Segmentação de Texto em Chunks |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve dividir o texto plano de um documento em segmentos contínuos (chunks) com tamanho máximo de 512 tokens e overlap de 50 tokens entre chunks consecutivos. A segmentação deve ocorrer preferencialmente em limites de parágrafo ou frase, evitando a quebra no meio de uma sentença. Cada chunk deve receber um identificador UUID, número de ordem sequencial, referência ao documento de origem, página inicial e página final. O sistema deve garantir que nenhum texto do documento original seja omitido durante a segmentação.

### Condições de Aplicação

- Condição 1: O texto plano foi extraído com sucesso (REQ-FUNC-002).
- Condição 2: O texto possui no mínimo 1 palavra.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Arquiteto |
| **Requisito Pai** | REQ-FUNC-002 |
| **Requisitos Filhos** | REQ-FUNC-004, REQ-FUNC-005 |
| **Casos de Uso / Histórias Relacionadas** | UC-003: Segmentar documento em chunks |

---

## Justificativa (Rationale)

O modelo de linguagem (SLM) possui contexto limitado. A segmentação em chunks de tamanho controlado permite que cada unidade seja processada individualmente sem perda de contexto. O overlap garante continuidade semântica entre chunks adjacentes, evitando que informações que cruzam limites de segmento sejam perdidas.

---

## Critérios de Verificação e Aceitação

### Método de Verificação
- [x] Teste
- [ ] Inspeção / Revisão
- [ ] Demonstração
- [ ] Análise
- [ ] Simulação

### Critérios de Aceitação (Gherkin / BDD)
```gherkin
Funcionalidade: Segmentação de texto em chunks
  Cenário: Documento de 5000 palavras
    Dado que o texto plano contém 5000 palavras
    Quando o sistema executa a segmentação
    Então o número de chunks gerados está entre 15 e 30
    E cada chunk possui no máximo 512 tokens
    E cada chunk consecutivo compartilha 50 tokens com o anterior
    E a concatenação de todos os chunks (removendo overlaps) contém 100% do texto original

  Cenário: Documento de 100 palavras
    Dado que o texto plano contém 100 palavras
    Quando o sistema executa a segmentação
    Então é gerado exatamente 1 chunk
    E o chunk contém as 100 palavras do texto original
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-011 | Documento de 5000 palavras | 15-30 chunks, <= 512 tokens cada, 50 tokens overlap |
| TEST-012 | Documento de 100 palavras | 1 chunk, texto completo preservado |
| TEST-013 | Concatenação de chunks removendo overlap | 100% do texto original recuperado |
| TEST-014 | Quebra em limite de frase | Nenhuma sentença cortada ao meio |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para processamento pelo SLM. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Descreve o que, não como implementar o algoritmo. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Tamanhos (512, 50) e critérios são numéricos. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui identificação, ordenação e rastreabilidade. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na segmentação. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com LangChain RecursiveCharacterTextSplitter. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por contagem de tokens e concatenação. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à limitação de contexto do SLM. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-002 (texto plano extraído).
- A contagem de tokens utiliza o tokenizador do modelo SLM (via llama-cpp-python).

### Notas e Suposições
- O tokenizador do modelo SLM é utilizado para contagem precisa de tokens.
- Documentos com menos de 512 tokens geram um único chunk sem overlap.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Documentação LangChain RecursiveCharacterTextSplitter

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Rafael Adolfo Silva Ferreira | Criação inicial |
