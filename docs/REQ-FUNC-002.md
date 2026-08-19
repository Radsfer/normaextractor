# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-002` |
| **Nome** | Conversão de Documentos para Texto Plano |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve converter o conteúdo de arquivos PDF, DOCX e TXT em texto plano Unicode (UTF-8). Para arquivos PDF, o sistema deve extrair o texto mantendo a ordem dos parágrafos e identificando quebras de página. Para arquivos DOCX, o sistema deve extrair o texto dos parágrafos, ignorando cabeçalhos, rodapés e notas de rodapé. Para arquivos TXT, o sistema deve ler o conteúdo diretamente. O texto extraído deve ser armazenado temporariamente em memória e persistido em arquivo de texto no sistema de arquivos. O sistema deve calcular o hash SHA-256 do texto extraído e registrar o número total de palavras e de páginas no banco de dados relacional.

### Condições de Aplicação

- Condição 1: O documento foi recebido e validado com sucesso (REQ-FUNC-001).
- Condição 2: O arquivo não está corrompido e possui conteúdo textual legível.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Analista jurídico |
| **Requisito Pai** | REQ-FUNC-001 |
| **Requisitos Filhos** | REQ-FUNC-003 |
| **Casos de Uso / Histórias Relacionadas** | UC-002: Converter documento para texto |

---

## Justificativa (Rationale)

O pipeline de processamento depende de texto plano para segmentação, geração de embeddings e extração estruturada. A conversão precisa e fiel do conteúdo original é pré-requisito para a qualidade das etapas subsequentes.

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
Funcionalidade: Conversão de documentos para texto plano
  Cenário: Conversão de PDF de 10 páginas
    Dado que o documento PDF de 10 páginas foi recebido
    Quando o sistema executa a conversão
    Então o texto extraído contém no mínimo 90% das palavras do documento original
    E o número de páginas registrado é igual a 10
    E o hash SHA-256 do texto é calculado e armazenado

  Cenário: Conversão de DOCX com cabeçalho e rodapé
    Dado que o documento DOCX possui cabeçalho, rodapé e notas de rodapé
    Quando o sistema executa a conversão
    Então o texto extraído não contém o conteúdo do cabeçalho
    E o texto extraído não contém o conteúdo do rodapé
    E o texto extraído não contém as notas de rodapé

  Cenário: Falha na conversão de PDF corrompido
    Dado que o documento PDF está corrompido
    Quando o sistema tenta a conversão
    Então o sistema registra o status "erro" no banco de dados
    E o campo "error_message" contém a descrição da exceção
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-007 | Conversão de PDF de 10 páginas (5000 palavras) | >= 90% de palavras recuperadas, 10 páginas registradas |
| TEST-008 | Conversão de DOCX com cabeçalho e rodapé | Texto limpo, sem elementos de layout |
| TEST-009 | Conversão de TXT com 1000 palavras | Texto idêntico ao original, 1000 palavras registradas |
| TEST-010 | Conversão de PDF corrompido | Status "erro", mensagem de exceção registrada |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Pré-requisito para todo o pipeline de processamento. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Descreve o que é necessário, não como implementar. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Percentual (90%), formatos e elementos ignorados são claros. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui formatos, tratamento de elementos e persistência. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na conversão de formato. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com PyPDF2, python-docx e leitura de arquivo. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por comparação de contagem de palavras. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de texto processável. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-001 (arquivo recebido e validado).
- Depende das bibliotecas PyPDF2 (>= 3.0.0) e python-docx (>= 0.8.11).

### Notas e Suposições
- O PDF não é uma imagem escaneada (sem OCR). Versão futura tratará OCR.
- O DOCX segue a especificação OOXML padrão.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- Anexo: Arquivos de teste com contagem de palavras conhecida

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
