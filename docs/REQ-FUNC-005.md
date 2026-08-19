# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-005` |
| **Nome** | Armazenamento Vetorial no ChromaDB |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve persistir cada chunk, seu embedding e seus metadados no banco de dados vetorial ChromaDB em modo embedded. Cada registro no ChromaDB deve conter: identificador do chunk (UUID), texto completo do chunk, embedding vetorial (384 dimensões), identificador do documento de origem (UUID), número de ordem do chunk, página inicial e página final. O sistema deve garantir que o ChromaDB utilize a função de distância cosseno para comparação de similaridade. A persistência deve ocorrer em diretório local do sistema de arquivos da VPS, permitindo backup por cópia de arquivos.

### Condições de Aplicação

- Condição 1: O embedding foi gerado com sucesso (REQ-FUNC-004).
- Condição 2: O ChromaDB está inicializado e o diretório de persistência possui permissão de escrita.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Arquiteto |
| **Requisito Pai** | REQ-FUNC-004 |
| **Requisitos Filhos** | REQ-FUNC-009 |
| **Casos de Uso / Histórias Relacionadas** | UC-005: Indexar chunks no banco vetorial |

---

## Justificativa (Rationale)

O banco vetorial é o repositório que permite a recuperação semântica de trechos relevantes durante a consulta RAG. Sem persistência vetorial, cada consulta exigiria reprocessamento completo dos documentos, tornando o sistema inviável.

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
Funcionalidade: Armazenamento vetorial no ChromaDB
  Cenário: Inserção de chunk com embedding
    Dado que um chunk com embedding válido foi gerado
    Quando o sistema persiste o chunk no ChromaDB
    Então o registro é recuperável pelo identificador do chunk
    E o texto recuperado é idêntico ao texto original
    E o embedding recuperado possui 384 dimensões
    E os metadados contêm o document_id e o número de ordem

  Cenário: Busca por similaridade
    Dado que 10 chunks de um documento sobre "Lei de Proteção de Dados" foram persistidos
    Quando o sistema consulta o ChromaDB com o texto "obrigações do controlador"
    Então o sistema retorna os 5 chunks mais similares
    E o primeiro resultado possui score de similaridade >= 0.70
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-019 | Inserção e recuperação de chunk | Texto e embedding idênticos aos originais |
| TEST-020 | Busca por similaridade semântica | 5 resultados, score >= 0.70 no primeiro |
| TEST-021 | Persistência após reinicialização | Dados recuperados após restart do ChromaDB |
| TEST-022 | Metadados completos | document_id, order, page_start, page_end presentes |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para RAG e consulta semântica. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica ChromaDB, mas não impõe design de schema. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Campos, dimensões e função de distância são explícitos. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui metadados, função de distância e persistência. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente no armazenamento vetorial. |
| **Feasible (Factível)** | [x] Sim [ ] Não | ChromaDB embedded opera sem servidor externo. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por inserção, recuperação e busca. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de busca semântica. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-004 (embeddings gerados).
- Depende da biblioteca ChromaDB em modo embedded.
- O diretório de persistência do ChromaDB deve estar em volume com espaço suficiente (mínimo 2 GB).

### Notas e Suposições
- O ChromaDB em modo embedded utiliza SQLite para metadados e arquivo binário para vetores.
- A função de distância cosseno é configurada na criação da collection.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Documentação ChromaDB

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
