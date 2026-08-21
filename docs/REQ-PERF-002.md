# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-PERF-002` |
| **Nome** | Latência de Resposta do Chat RAG |
| **Tipo** | `Performance` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O tempo entre o envio de uma pergunta pelo usuário e o recebimento do primeiro token da resposta pelo cliente (Time to First Token, TTFT) deve ser inferior a 3 segundos, para consultas sobre bases de dados com até 100 documentos processados (aproximadamente 1500 chunks indexados no ChromaDB). O TTFT deve ser medido como a média aritmética de 10 consultas consecutivas em ambiente de teste com VPS de 4 GB de RAM e 2 vCPUs. O TTFT inclui: recebimento da requisição, geração do embedding da pergunta, busca vetorial no ChromaDB, montagem do prompt de contexto e início da geração pelo SLM. O TTFT não inclui o tempo de download da resposta pelo cliente nem a renderização da interface.

### Condições de Aplicação

- Condição 1: O banco vetorial contém no máximo 1500 chunks (equivalente a 100 documentos de 10 páginas).
- Condição 2: A VPS possui 4 GB de RAM e 2 vCPUs.
- Condição 3: O modelo SLM e o modelo de embeddings estão previamente carregados na RAM.
- Condição 4: O sistema não está processando outros documentos simultaneamente.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Analista jurídico |
| **Requisito Pai** | Não aplicável |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-014: Receber resposta rápida no chat |

---

## Justificativa (Rationale)

Um TTFT superior a 3 segundos cria a percepção de lentidão e desencoraja o uso do chat. O limite de 3 segundos é um padrão de usabilidade para interfaces conversacionais e é factível com busca vetorial em CPU e SLM de 3B parâmetros.

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
Funcionalidade: Latência de resposta do chat RAG
  Cenário: Consulta em base com 100 documentos
    Dado que o banco vetorial contém 1500 chunks de 100 documentos
    E o sistema executa em VPS com 4 GB de RAM e 2 vCPUs
    Quando o usuário envia 10 perguntas consecutivas
    Então a média aritmética do TTFT é inferior a 3 segundos
    E o TTFT máximo entre as 10 consultas é inferior a 5 segundos
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-055 | 10 consultas em base de 100 documentos | Média TTFT < 3s, máximo < 5s |
| TEST-056 | Consulta com embedding de pergunta | Tempo de embedding < 1s |
| TEST-057 | Busca vetorial em 1500 chunks | Tempo de busca < 1s |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para experiência de uso do chat. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica limite numérico, não impõe otimização. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | 3s, 100 documentos, 1500 chunks, 4GB, média de 10 consultas. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui escopo do tempo, ambiente e método de medição. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na latência do chat. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Embedding (~0.5s) + busca vetorial (~0.5s) + primeira token (~1s) = ~2s. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por cronometragem de 10 consultas. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à expectativa de responsividade do usuário. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-009 (consulta RAG funcional).
- Depende do REQ-FUNC-005 (banco vetorial com chunks indexados).
- A medição deve ser realizada em ambiente isolado.

### Notas e Suposições
- A busca vetorial em ChromaDB com 1500 chunks em CPU leva menos de 1 segundo.
- A geração do embedding da pergunta leva menos de 0.5 segundo.
- O tempo até o primeiro token do SLM depende do tamanho do prompt de contexto (5 chunks).

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- Anexo: Script de benchmark de latência do chat (anexo técnico)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Rafael Adolfo Silva Ferreira | Criação inicial |
