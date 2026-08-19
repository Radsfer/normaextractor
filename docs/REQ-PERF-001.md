# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-PERF-001` |
| **Nome** | Tempo de Processamento de Documentos |
| **Tipo** | `Performance` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve processar um documento de 10 páginas (aproximadamente 5000 palavras) em no máximo 180 segundos, medidos desde o momento do recebimento do arquivo via upload até a conclusão da extração estruturada de todos os chunks e persistência no banco relacional. O tempo de 180 segundos deve ser medido como a média aritmética de 5 execuções consecutivas em ambiente de teste com VPS de 4 GB de RAM e 2 vCPUs. O tempo inclui: validação do arquivo, conversão para texto plano, segmentação em chunks, geração de embeddings, inserção no ChromaDB, extração estruturada por chunk, validação Pydantic e persistência no SQLite. O tempo não inclui o download do arquivo pelo usuário nem a renderização do dashboard.

### Condições de Aplicação

- Condição 1: O documento possui 10 páginas e aproximadamente 5000 palavras.
- Condição 2: A VPS possui 4 GB de RAM e 2 vCPUs.
- Condição 3: O modelo SLM e o modelo de embeddings estão previamente carregados na RAM.
- Condição 4: O sistema não está processando outros documentos simultaneamente.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Arquiteto |
| **Requisito Pai** | Não aplicável |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-013: Processar documento em tempo aceitável |

---

## Justificativa (Rationale)

Um tempo de processamento superior a 180 segundos (3 minutos) por documento de 10 páginas torna o sistema impraticável para volumes moderados de documentos. O limite de 180 segundos equilibra a restrição de hardware (VPS 4GB, CPU) com a expectativa de produtividade do analista jurídico.

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
Funcionalidade: Tempo de processamento de documentos
  Cenário: Documento de 10 páginas em VPS 4GB
    Dado que o sistema está executando em VPS com 4 GB de RAM e 2 vCPUs
    E o documento de teste possui 10 páginas e 5000 palavras
    E os modelos estão carregados na RAM
    Quando o sistema processa o documento 5 vezes consecutivas
    Então a média aritmética dos tempos de processamento é inferior a 180 segundos
    E o desvio padrão dos tempos é inferior a 20 segundos
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-052 | Processamento de PDF 10 páginas (5 execuções) | Média < 180s, desvio padrão < 20s |
| TEST-053 | Processamento de DOCX 10 páginas (5 execuções) | Média < 180s, desvio padrão < 20s |
| TEST-054 | Processamento de TXT 5000 palavras (5 execuções) | Média < 180s, desvio padrão < 20s |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para viabilidade do produto. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica limite numérico, não impõe otimização específica. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | 180s, 10 páginas, 5000 palavras, 4GB, 2 vCPUs, média de 5 execuções. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui escopo do tempo, ambiente e método de medição. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente no tempo de processamento. |
| **Feasible (Factível)** | [x] Sim [ ] Não | SLM 3B em CPU processa ~20 tokens/s; 5000 palavras em ~15 chunks = ~180s viável. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por cronometragem de 5 execuções. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à expectativa de produtividade do usuário. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende de todos os requisitos funcionais do pipeline (REQ-FUNC-001 a REQ-FUNC-008).
- A medição deve ser realizada em ambiente isolado (sem outros processos concorrentes).
- O tempo de carregamento inicial dos modelos na RAM não é contabilizado.

### Notas e Suposições
- O documento de 10 páginas gera aproximadamente 15 chunks de 512 tokens.
- Cada chunk requer ~10 segundos de inferência no SLM (3B Q4, CPU).
- A geração de embeddings consome ~1 segundo por chunk.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- Anexo: Script de benchmark de tempo de processamento (anexo técnico)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
