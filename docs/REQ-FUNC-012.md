# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-012` |
| **Nome** | Streaming de Respostas do Chat via SSE |
| **Tipo** | `Funcional` |
| **Prioridade** | `Desejável` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve transmitir a resposta gerada pelo modelo SLM durante a consulta RAG (REQ-FUNC-009) em formato de streaming, utilizando o protocolo Server-Sent Events (SSE). O primeiro token da resposta deve ser enviado ao cliente em no máximo 3 segundos após o recebimento da pergunta. Os tokens subsequentes devem ser enviados à medida que são gerados pelo modelo, sem buffering completo da resposta. Após a conclusão da geração da resposta, o sistema deve enviar um evento final contendo as fontes (array de objetos com document_id, nome do arquivo, número da página e trecho resumido). O cliente deve exibir os tokens em tempo real na interface de chat, com indicador visual de processamento ativo durante a geração. A conexão SSE deve ser encerrada automaticamente após o envio do evento de fontes.

### Condições de Aplicação

- Condição 1: A consulta RAG foi iniciada com sucesso (REQ-FUNC-009).
- Condição 2: O modelo SLM está gerando tokens.
- Condição 3: O cliente suporta conexão HTTP persistente para SSE.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Analista jurídico |
| **Requisito Pai** | REQ-FUNC-009 |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-012: Receber resposta em tempo real |

---

## Justificativa (Rationale)

A inferência em CPU com modelo SLM pode levar 30 a 60 segundos para gerar uma resposta completa. O streaming melhora a percepção de performance do usuário, fornecendo feedback imediato e reduzindo a sensação de espera. A exibição em tempo real é padrão em interfaces de chat modernas.

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
Funcionalidade: Streaming de respostas do chat via SSE
  Cenário: Resposta com streaming
    Dado que o usuário enviou uma pergunta válida
    Quando o sistema inicia a geração da resposta pelo SLM
    Então o primeiro evento SSE é recebido pelo cliente em menos de 3 segundos
    E os tokens são exibidos na interface em tempo real
    E um indicador visual de processamento está ativo durante a geração

  Cenário: Conclusão da resposta com fontes
    Dado que o SLM concluiu a geração da resposta
    Quando o último token é enviado
    Então o sistema envia um evento final com as fontes
    E a conexão SSE é encerrada automaticamente
    E o indicador visual de processamento é desativado

  Cenário: Interrupção pelo usuário
    Dado que o usuário clicou no botão de cancelar durante a geração
    Quando o cliente encerra a conexão SSE
    Então o backend interrompe a geração do SLM
    E libera os recursos de inferência
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-048 | Primeiro token em < 3s | Evento SSE recebido em menos de 3 segundos |
| TEST-049 | Streaming contínuo | Tokens recebidos sequencialmente, sem buffering |
| TEST-050 | Evento final com fontes | Array de fontes recebido após conclusão |
| TEST-051 | Cancelamento pelo usuário | Geração interrompida, recursos liberados |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Não é essencial para funcionalidade, mas essencial para UX. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Descreve o comportamento, não impõe biblioteca de frontend. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | 3 segundos, SSE, evento final, cancelamento são claros. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui início, meio, fim e cancelamento. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente no mecanismo de streaming. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com FastAPI StreamingResponse + EventSource. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por medição de tempo e inspeção de eventos SSE. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de feedback imediato ao usuário. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-009 (consulta RAG iniciada).
- Depende do suporte a SSE no FastAPI (StreamingResponse).
- O cliente React deve utilizar EventSource API nativa.

### Notas e Suposições
- O modelo SLM suporta geração token por token via llama-cpp-python (stream=True).
- A latência de 3 segundos para o primeiro token inclui a busca vetorial e o tempo de carregamento do contexto no modelo.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: FastAPI StreamingResponse documentation
- REF-003: MDN EventSource API

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
