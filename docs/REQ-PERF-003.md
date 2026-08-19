# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-PERF-003` |
| **Nome** | Consumo Máximo de RAM durante Processamento |
| **Tipo** | `Performance` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O consumo de memória RAM do processo do sistema (backend + SLM + embeddings + ChromaDB + SQLite) durante o processamento de um documento de 10 páginas não deve exceder 3.2 GB. O consumo deve ser medido via biblioteca psutil no processo Python principal, amostrado a cada 1 segundo durante o processamento completo do documento. O valor de pico (máximo entre as amostras) deve ser inferior a 3.2 GB. O consumo de RAM do sistema operacional e de processos externos não é contabilizado. A medição deve ser realizada em ambiente de teste com VPS de 4 GB de RAM e 2 vCPUs, com os modelos previamente carregados na RAM.

### Condições de Aplicação

- Condição 1: O documento possui 10 páginas e aproximadamente 5000 palavras.
- Condição 2: A VPS possui 4 GB de RAM totais.
- Condição 3: O sistema não está processando outros documentos simultaneamente.
- Condição 4: O swap da VPS está desativado durante o teste.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Arquiteto |
| **Requisito Pai** | Não aplicável |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-015: Operar dentro de limites de hardware |

---

## Justificativa (Rationale)

A VPS possui 4 GB de RAM totais. O sistema operacional consome aproximadamente 500 MB. Reservar 3.2 GB para o processo principal garante uma folga de 300 MB para picos ocasionais e evita ativação de swap, que degradaria drasticamente a performance.

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
Funcionalidade: Consumo máximo de RAM durante processamento
  Cenário: Processamento de documento de 10 páginas
    Dado que a VPS possui 4 GB de RAM e swap desativado
    E o documento de teste possui 10 páginas e 5000 palavras
    Quando o sistema processa o documento completo
    Então o consumo de RAM do processo principal, medido a cada 1 segundo, não excede 3.2 GB em nenhum momento
    E o consumo médio de RAM durante o processamento é inferior a 2.8 GB
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-058 | Consumo de RAM durante processamento PDF | Pico < 3.2 GB, média < 2.8 GB |
| TEST-059 | Consumo de RAM durante processamento DOCX | Pico < 3.2 GB, média < 2.8 GB |
| TEST-060 | Consumo de RAM durante consulta RAG | Pico < 3.2 GB durante inferência |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para operação na VPS de 4GB. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica limite numérico, não impõe gestão de memória específica. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | 3.2 GB, 10 páginas, psutil, amostragem a cada 1s, swap desativado. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui método de medição, ambiente e condições. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente no consumo de RAM. |
| **Feasible (Factível)** | [x] Sim [ ] Não | SLM 3B Q4 (~1.8GB) + embeddings (~400MB) + backend (~500MB) = ~2.7GB. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por psutil durante execução. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à restrição de hardware da VPS. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende de todos os requisitos funcionais do pipeline.
- A biblioteca psutil deve estar instalada no ambiente Python.
- O swap deve ser desativado para medição precisa (sem memória virtual).

### Notas e Suposições
- O modelo SLM 3B Q4_K_M consome ~1.8 GB de RAM quando carregado.
- O modelo de embeddings consome ~400 MB de RAM quando carregado.
- O backend consome ~500 MB de RAM em operação normal.
- ChromaDB embedded consome ~200 MB de RAM com 1500 chunks.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- Anexo: Script de monitoramento de RAM com psutil (anexo técnico)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
