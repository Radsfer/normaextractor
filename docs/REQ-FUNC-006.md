# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-006` |
| **Nome** | Extração Estruturada de Cláusulas Normativas |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve processar cada chunk de texto utilizando o modelo de linguagem local (SLM) para identificar e extrair as seguintes informações estruturadas: tipo de cláusula (obrigação, proibição, direito, permissão, penalidade), sujeito da norma (pessoa física, pessoa jurídica, órgão público, entidade regulada), ação descrita (verbo ou expressão que define o comportamento exigido ou vedado), prazo (data, período ou condição temporal, quando presente), base legal (artigo, parágrafo, inciso ou alínea de origem, quando identificável) e penalidade (sanção ou consequência do descumprimento, quando presente). O sistema deve estruturar a extração no formato JSON, validar contra o schema Pydantic definido e armazenar o resultado. O sistema deve calcular a métrica de coverage como a proporção de campos obrigatórios (tipo, sujeito, ação) preenchidos em relação ao total de chunks analisados. O coverage mínimo aceitável é de 85% para documentos com estrutura normativa padrão.

### Condições de Aplicação

- Condição 1: O chunk está armazenado no ChromaDB (REQ-FUNC-005).
- Condição 2: O modelo SLM está carregado na memória RAM.
- Condição 3: O chunk contém texto em língua portuguesa.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Analista jurídico |
| **Requisito Pai** | REQ-FUNC-005 |
| **Requisitos Filhos** | REQ-FUNC-007, REQ-FUNC-010 |
| **Casos de Uso / Histórias Relacionadas** | UC-006: Extrair cláusulas de documento |

---

## Justificativa (Rationale)

A análise manual de documentos normativos para identificar obrigações, prazos e penalidades é demorada e sujeita a inconsistência entre analistas. A extração automatizada padroniza a estruturação, reduz o tempo de análise e permite auditoria e rastreabilidade.

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
Funcionalidade: Extração estruturada de cláusulas normativas
  Cenário: Documento de teste com 3 cláusulas conhecidas
    Dado que o documento de teste contém 3 cláusulas normativas identificadas manualmente
    Quando o sistema executa a extração estruturada
    Então o coverage de campos obrigatórios é >= 85%
    E cada extração contém os campos tipo, sujeito e ação preenchidos
    E as extrações referenciam o chunk_id de origem

  Cenário: Chunk sem conteúdo normativo
    Dado que o chunk contém apenas texto expositivo sem norma
    Quando o sistema executa a extração
    Então o sistema retorna um objeto JSON com campos nulos
    E o campo "tipo" possui o valor "não_identificado"
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-023 | Extração de documento com 3 cláusulas | Coverage >= 85%, campos obrigatórios preenchidos |
| TEST-024 | Extração de chunk sem norma | JSON com campos nulos, tipo = "não_identificado" |
| TEST-025 | Validação de schema Pydantic | JSON inválido é rejeitado com mensagem de erro |
| TEST-026 | Rastreabilidade de origem | Cada extração contém chunk_id e document_id |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Core do produto. Sem extração, o sistema não atende ao propósito. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Descreve os campos, não impõe algoritmo de NLP. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Campos, valores aceitáveis e coverage são definidos. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui validação, métrica e condições de aplicação. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na extração estruturada. |
| **Feasible (Factível)** | [x] Sim [ ] Não | SLM de 3B parâmetros executa extração em CPU. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por documento de teste com ground truth. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de estruturação de documentos legais. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-005 (chunks indexados).
- Depende do modelo SLM carregado (~1.8 GB RAM).
- A qualidade da extração depende da clareza do texto normativo no documento.

### Notas e Suposições
- O modelo SLM foi ajustado com prompts específicos para extração de campos legais.
- Documentos com linguagem coloquial ou altamente técnica fora do domínio jurídico podem apresentar coverage inferior a 85%.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Schema Pydantic de extração (anexo técnico)
- Anexo: Documento de teste com ground truth anotado manualmente

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Rafael Adolfo Silva Ferreira | Criação inicial |
