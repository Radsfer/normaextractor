# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-008` |
| **Nome** | Persistência de Extrações no Banco Relacional |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve persistir no banco de dados relacional SQLite cada extração validada com sucesso (REQ-FUNC-007). O registro deve conter: identificador UUID da extração, identificador UUID do chunk de origem, identificador UUID do documento de origem, campos extraídos (tipo, sujeito, ação, prazo, base_legal, penalidade), timestamp da extração (UTC), versão do modelo SLM utilizado, versão do schema Pydantic aplicado e flag de validação (booleano). O sistema deve garantir integridade referencial entre as tabelas de documentos, chunks e extrações por meio de chaves estrangeiras. O sistema deve permitir consulta das extrações por documento, por tipo de cláusula ou por sujeito, com tempo de resposta inferior a 1 segundo para bases com até 1000 extrações.

### Condições de Aplicação

- Condição 1: A extração foi validada com sucesso (REQ-FUNC-007).
- Condição 2: O banco SQLite está inicializado e a conexão está ativa.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Arquiteto |
| **Requisito Pai** | REQ-FUNC-007 |
| **Requisitos Filhos** | REQ-FUNC-010 |
| **Casos de Uso / Histórias Relacionadas** | UC-008: Consultar extrações estruturadas |

---

## Justificativa (Rationale)

O banco relacional armazena os dados estruturados finais que alimentam o dashboard e as métricas de coverage. A integridade referencial garante que cada extração possa ser rastreada até o chunk e documento de origem, permitindo auditoria e correção.

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
Funcionalidade: Persistência de extrações no banco relacional
  Cenário: Extração válida persistida
    Dado que uma extração foi validada com sucesso
    Quando o sistema persiste a extração no SQLite
    Então o registro é recuperável pelo UUID da extração
    E o registro contém o chunk_id e document_id de origem
    E o timestamp está no formato ISO 8601 UTC

  Cenário: Consulta por documento
    Dado que 50 extrações de um documento foram persistidas
    Quando o sistema consulta por document_id
    Então o sistema retorna as 50 extrações em menos de 1 segundo

  Cenário: Integridade referencial
    Dado que uma extração referencia um chunk_id
    Quando o chunk é excluído do banco
    Então a extração associada é excluída em cascata
    Ou o sistema impede a exclusão do chunk
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-031 | Persistência de extração válida | Recuperável, metadados completos, < 1s |
| TEST-032 | Consulta por document_id | 50 registros, tempo < 1s |
| TEST-033 | Consulta por tipo="obrigação" | Apenas registros com tipo="obrigação" |
| TEST-034 | Integridade referencial | Exclusão em cascata ou impedimento de exclusão |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para dashboard e métricas. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica campos, não impõe design de tabela. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Campos, tipos, formato de timestamp e tempo de resposta são claros. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui integridade referencial e consulta. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na persistência relacional. |
| **Feasible (Factível)** | [x] Sim [ ] Não | SQLite atende a volume de 1000 extrações com performance. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por inserção, consulta e medição de tempo. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de dados estruturados consultáveis. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-007 (extração validada).
- Depende do SQLAlchemy (>= 2.0) para ORM e SQLite.
- O banco SQLite deve ser configurado com WAL (Write-Ahead Logging) para concorrência.

### Notas e Suposições
- O volume de dados na versão 1.0 não excede 1000 extrações por mês.
- A migração de schema é gerenciada por Alembic.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Diagrama ER (anexo técnico)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Rafael Adolfo Silva Ferreira | Criação inicial |
