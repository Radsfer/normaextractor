# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-010` |
| **Nome** | Dashboard de Métricas de Qualidade |
| **Tipo** | `Funcional` |
| **Prioridade** | `Desejável` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve exibir em interface web um dashboard com as seguintes métricas calculadas automaticamente a partir dos dados persistidos: coverage (proporção de chunks com extração válida em relação ao total de chunks processados, expressa em porcentagem), consistência (proporção de extrações que passaram na validação do schema Pydantic na primeira tentativa, expressa em porcentagem) e latência média (tempo médio de processamento de um documento, desde o upload até a conclusão da extração, expresso em segundos). O dashboard deve permitir filtrar as métricas por documento individual, por período de tempo (data inicial e data final) e por tipo de documento (PDF, DOCX, TXT). As métricas devem ser atualizadas em tempo real a cada conclusão de processamento de um documento, sem necessidade de recarregar a página.

### Condições de Aplicação

- Condição 1: O usuário está autenticado no sistema.
- Condição 2: O banco relacional contém no mínimo 1 documento processado.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Administrador |
| **Requisito Pai** | REQ-FUNC-008 |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-010: Visualizar métricas de qualidade |

---

## Justificativa (Rationale)

O desenvolvedor e o administrador do sistema necessitam monitorar a qualidade do pipeline de extração para identificar regressões, ajustar prompts do SLM e decidir sobre a substituição do modelo. O analista jurídico utiliza o coverage para avaliar a confiabilidade dos dados extraídos de um documento específico.

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
Funcionalidade: Dashboard de métricas de qualidade
  Cenário: Exibição de métricas gerais
    Dado que 10 documentos foram processados no sistema
    Quando o usuário acessa o dashboard
    Então o dashboard exibe o valor numérico do coverage
    E o dashboard exibe o valor numérico da consistência
    E o dashboard exibe o valor numérico da latência média
    E os valores são atualizados automaticamente após cada novo documento processado

  Cenário: Filtro por documento individual
    Dado que o usuário selecionou um documento específico no filtro
    Quando o dashboard aplica o filtro
    Então o coverage exibido refere-se apenas ao documento selecionado
    E a latência exibida refere-se apenas ao documento selecionado

  Cenário: Filtro por período
    Dado que o usuário informou data inicial "01/08/2026" e data final "19/08/2026"
    Quando o dashboard aplica o filtro
    Então as métricas consideram apenas documentos processados no período informado
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-039 | Exibição de métricas com 10 documentos | Coverage, consistência e latência numéricos visíveis |
| TEST-040 | Atualização em tempo real | Novo documento processado, métricas atualizadas sem reload |
| TEST-041 | Filtro por documento | Métricas restritas ao documento selecionado |
| TEST-042 | Filtro por período | Métricas restritas ao intervalo de datas |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Não é essencial para operação, mas essencial para monitoramento. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Descreve as métricas, não impõe biblioteca de gráficos. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Fórmulas de coverage, consistência e latência são definidas. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui filtros e atualização em tempo real. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na exibição de métricas. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com React + WebSocket/SSE + SQLite. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por inserção de dados de teste e verificação dos valores. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de monitoramento de qualidade. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-008 (extrações persistidas no banco relacional).
- Depende de conexão WebSocket ou SSE para atualização em tempo real.
- As métricas são calculadas no backend a partir de consultas SQL ao SQLite.

### Notas e Suposições
- Coverage = (chunks com extração válida / total de chunks) * 100
- Consistência = (extrações válidas na primeira tentativa / total de extrações) * 100
- Latência média = média aritmética dos tempos de processamento por documento

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- Anexo: Fórmulas de cálculo das métricas (anexo técnico)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Rafael Adolfo Silva Ferreira | Criação inicial |
