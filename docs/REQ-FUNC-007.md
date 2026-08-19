# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-007` |
| **Nome** | Validação de Extrações via Schema Pydantic |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve validar cada objeto JSON produzido pela extração estruturada (REQ-FUNC-006) contra um schema Pydantic predefinido. O schema deve definir os campos obrigatórios (tipo, sujeito, ação), os campos opcionais (prazo, base_legal, penalidade), os tipos de dados permitidos para cada campo (string, string | null) e as enumerações de valores aceitáveis para o campo "tipo" (obrigação, proibição, direito, permissão, penalidade, não_identificado). O sistema deve rejeitar extrações que não atendam ao schema, registrar o erro no log de processamento e marcar o chunk como "extração falha" no banco de dados relacional. O sistema deve permitir até 3 tentativas de extração por chunk, ajustando o prompt do SLM em cada tentativa. Após 3 tentativas falhas, o chunk é marcado como "não extraível" e o processamento continua com os demais chunks.

### Condições de Aplicação

- Condição 1: A extração estruturada foi executada para o chunk (REQ-FUNC-006).
- Condição 2: O schema Pydantic está carregado na memória do processo backend.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Arquiteto |
| **Requisito Pai** | REQ-FUNC-006 |
| **Requisitos Filhos** | REQ-FUNC-008 |
| **Casos de Uso / Histórias Relacionadas** | UC-007: Validar extrações |

---

## Justificativa (Rationale)

A saída de modelos de linguagem é não determinística. Sem validação estruturada, o sistema pode persistir dados malformados, corrompendo o dashboard e as métricas de coverage. O schema Pydantic garante integridade dos dados e permite retry controlado.

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
Funcionalidade: Validação de extrações via schema Pydantic
  Cenário: Extração válida
    Dado que o SLM retornou um JSON com tipo="obrigação", sujeito="empresa", ação="informar o titular"
    Quando o sistema valida o JSON contra o schema Pydantic
    Então o JSON é aceito
    E o chunk é marcado como "extração válida"

  Cenário: Extração com campo obrigatório ausente
    Dado que o SLM retornou um JSON sem o campo "sujeito"
    Quando o sistema valida o JSON contra o schema Pydantic
    Então o JSON é rejeitado
    E o sistema executa uma nova tentativa de extração com prompt ajustado
    E o número de tentativas é incrementado

  Cenário: Falha após 3 tentativas
    Dado que o chunk falhou na validação em 3 tentativas consecutivas
    Quando o sistema tenta a quarta validação
    Então o chunk é marcado como "não extraível"
    E o processamento continua com o próximo chunk
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-027 | JSON válido | Aceito, status "extração válida" |
| TEST-028 | JSON com campo obrigatório ausente | Rejeitado, retry com prompt ajustado |
| TEST-029 | JSON com tipo inválido | Rejeitado, retry com prompt ajustado |
| TEST-030 | 3 tentativas falhas consecutivas | Chunk marcado "não extraível", processamento continua |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para integridade dos dados. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Descreve o que validar, não como implementar parser. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Campos obrigatórios, opcionais, enumerações e retry são claros. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui tratamento de falha, retry e continuidade. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na validação estrutural. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Pydantic é biblioteca padrão, retry implementável. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por JSON de teste válido e inválido. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de dados confiáveis. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-006 (extração executada).
- Depende da biblioteca Pydantic (>= 2.0).
- O schema Pydantic deve ser versionado e armazenado no repositório.

### Notas e Suposições
- O SLM responde em formato JSON quando instruído por prompt de sistema.
- O ajuste de prompt entre tentativas consiste em reforçar a estrutura JSON esperada.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Schema Pydantic (anexo técnico)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
