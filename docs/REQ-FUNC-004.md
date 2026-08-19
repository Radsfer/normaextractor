# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-004` |
| **Nome** | Geração de Embeddings Semânticos |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve gerar um vetor de embedding de 384 dimensões para cada chunk de texto, utilizando o modelo all-MiniLM-L6-v2 executado localmente via sentence-transformers. O embedding deve ser representado como array de números de ponto flutuante de 32 bits. O sistema deve verificar que o vetor gerado possui exatamente 384 elementos, que todos os valores são finitos (não NaN, não infinito) e que a norma L2 do vetor é igual a 1.0 (normalizado). O tempo de geração do embedding para um chunk de 512 tokens não deve exceder 2 segundos em CPU.

### Condições de Aplicação

- Condição 1: O chunk foi criado com sucesso (REQ-FUNC-003).
- Condição 2: O modelo de embeddings está carregado na memória RAM.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Arquiteto |
| **Requisito Pai** | REQ-FUNC-003 |
| **Requisitos Filhos** | REQ-FUNC-005 |
| **Casos de Uso / Histórias Relacionadas** | UC-004: Gerar embeddings |

---

## Justificativa (Rationale)

Os embeddings semânticos permitem a busca por similaridade no banco vetorial, que é a base do mecanismo RAG. Sem embeddings, o chat não pode recuperar trechos relevantes dos documentos para fundamentar as respostas.

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
Funcionalidade: Geração de embeddings semânticos
  Cenário: Embedding de chunk de 512 tokens
    Dado que um chunk de 512 tokens foi criado
    Quando o sistema gera o embedding
    Então o vetor possui 384 dimensões
    E todos os valores do vetor são finitos
    E a norma L2 do vetor é igual a 1.0
    E o tempo de geração é inferior a 2 segundos

  Cenário: Embedding de chunk de 100 tokens
    Dado que um chunk de 100 tokens foi criado
    Quando o sistema gera o embedding
    Então o vetor possui 384 dimensões
    E todos os valores do vetor são finitos
    E a norma L2 do vetor é igual a 1.0
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-015 | Embedding de chunk 512 tokens | 384 dimensões, valores finitos, L2 = 1.0, < 2s |
| TEST-016 | Embedding de chunk 100 tokens | 384 dimensões, valores finitos, L2 = 1.0 |
| TEST-017 | Embedding de chunk com texto vazio | Exceção tratada, status de erro registrado |
| TEST-018 | Tempo de 100 embeddings sequenciais | Média < 2s por embedding |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para busca semântica e RAG. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica o modelo, mas não impõe implementação interna. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | 384 dimensões, L2 = 1.0, < 2s são mensuráveis. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui validação, normalização e limite de tempo. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na geração de embeddings. |
| **Feasible (Factível)** | [x] Sim [ ] Não | all-MiniLM-L6-v2 roda em CPU com ~400MB RAM. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por assert de dimensão e norma L2. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de busca semântica. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-003 (chunks criados).
- Depende do modelo all-MiniLM-L6-v2 (~400 MB RAM).
- O modelo deve ser baixado uma única vez durante a instalação.

### Notas e Suposições
- O modelo all-MiniLM-L6-v2 é utilizado por ser otimizado para CPU e ter tamanho reduzido.
- A normalização L2 é realizada automaticamente pelo sentence-transformers.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Documentação sentence-transformers
- REF-003: Hugging Face all-MiniLM-L6-v2

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
