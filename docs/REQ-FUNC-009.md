# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-009` |
| **Nome** | Consulta Interativa via RAG |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve receber perguntas em linguagem natural do usuário via interface web, gerar um embedding da pergunta utilizando o mesmo modelo all-MiniLM-L6-v2, consultar o ChromaDB para recuperar os 5 chunks mais semanticamente similares à pergunta, concatenar os textos dos chunks recuperados como contexto e submeter a pergunta juntamente com o contexto ao modelo SLM para geração de resposta. O sistema deve instruir o SLM a responder exclusivamente com base no contexto fornecido e a citar os trechos de origem. A resposta deve ser enviada ao usuário em formato de streaming (Server-Sent Events), token por token. A resposta deve incluir, no final, uma lista de fontes com: identificador do documento, título ou nome do arquivo, número da página e trecho resumido.

### Condições de Aplicação

- Condição 1: O usuário está autenticado no sistema.
- Condição 2: O banco vetorial contém no mínimo 1 chunk indexado.
- Condição 3: O modelo SLM está carregado na memória RAM.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Analista jurídico |
| **Requisito Pai** | REQ-FUNC-005 |
| **Requisitos Filhos** | REQ-FUNC-012 |
| **Casos de Uso / Histórias Relacionadas** | UC-009: Consultar documentos via chat |

---

## Justificativa (Rationale)

O analista jurídico precisa consultar rapidamente informações dispersas em múltiplos documentos normativos sem ler cada um integralmente. O RAG permite responder perguntas específicas fundamentadas em trechos reais dos documentos, reduzindo o risco de alucinação do modelo e garantindo rastreabilidade.

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
Funcionalidade: Consulta interativa via RAG
  Cenário: Pergunta sobre documento processado
    Dado que o banco vetorial contém chunks de um documento sobre "Lei Geral de Proteção de Dados"
    E o usuário envia a pergunta "Quais são as obrigações do controlador?"
    Quando o sistema executa a consulta RAG
    Então o sistema recupera 5 chunks relevantes do ChromaDB
    E a resposta gerada pelo SLM cita obrigações presentes nos chunks
    E a resposta inclui fontes com document_id, nome do arquivo e número da página

  Cenário: Pergunta sem resposta no contexto
    Dado que o usuário envia a pergunta "Qual é a capital da França?"
    E o banco vetorial contém apenas documentos sobre direito brasileiro
    Quando o sistema executa a consulta RAG
    Então o SLM responde que a informação não está presente nos documentos fornecidos
    E nenhuma fonte é citada
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-035 | Pergunta com resposta no contexto | 5 chunks recuperados, resposta fundamentada, fontes citadas |
| TEST-036 | Pergunta sem resposta no contexto | Resposta de recusa, nenhuma fonte citada |
| TEST-037 | Streaming de resposta | Primeiro token em < 3s, eventos SSE contínuos |
| TEST-038 | Fontes incluem página e trecho | Cada fonte contém document_id, nome, página, trecho |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para valor do produto. Sem RAG, o chat não tem utilidade. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Descreve o fluxo, não impõe implementação de LangChain. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Número de chunks (5), formato de resposta e fontes são claros. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui busca, geração, streaming e citação de fontes. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na consulta RAG. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com LangChain RetrievalQA + SSE. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por perguntas de teste com ground truth. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de consulta rápida a documentos. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-005 (chunks indexados no ChromaDB).
- Depende do modelo SLM carregado (~1.8 GB RAM).
- Depende do modelo de embeddings carregado (~400 MB RAM).
- O streaming SSE requer conexão HTTP persistente.

### Notas e Suposições
- O prompt do SLM inclui instrução de responder apenas com base no contexto e citar fontes.
- A recuperação de 5 chunks é um equilíbrio entre contexto suficiente e limitação de tokens do SLM.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Documentação LangChain RetrievalQA
- Anexo: Prompt de sistema RAG (anexo técnico)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Rafael Adolfo Silva Ferreira | Criação inicial |
