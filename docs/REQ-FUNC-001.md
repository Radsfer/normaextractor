# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-001` |
| **Nome** | Ingestão de Documentos Normativos |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve receber arquivos nos formatos PDF, DOCX e TXT, com tamanho entre 1 KB e 20 MB, por meio de interface web. O sistema deve validar o tipo MIME do arquivo e rejeitar arquivos com extensão ou tipo MIME não suportado. O sistema deve armazenar o arquivo recebido em diretório temporário e registrar metadados (nome original, tipo MIME, tamanho, data de upload, hash SHA-256) no banco de dados relacional. O sistema deve atribuir um identificador UUID ao documento e retornar esse identificador ao usuário.

### Condições de Aplicação

- Condição 1: O usuário está autenticado no sistema.
- Condição 2: O arquivo possui extensão .pdf, .docx ou .txt.
- Condição 3: O tamanho do arquivo está entre 1 KB e 20 MB.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Analista jurídico |
| **Requisito Pai** | Não aplicável |
| **Requisitos Filhos** | REQ-FUNC-002 |
| **Casos de Uso / Histórias Relacionadas** | UC-001: Enviar documento para análise |

---

## Justificativa (Rationale)

O analista jurídico necessita submeter documentos normativos para processamento automatizado. Sem a capacidade de receber arquivos nos formatos mais comuns de documentos legais, o sistema não atende ao propósito principal de extração estruturada.

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
Funcionalidade: Ingestão de documentos normativos
  Cenário: Upload de arquivo PDF válido
    Dado que o usuário está autenticado
    E selecionou um arquivo PDF de 500 KB
    Quando o usuário clica no botão de envio
    Então o sistema retorna o código HTTP 200
    E o corpo da resposta contém um campo "document_id" no formato UUID
    E o campo "status" possui o valor "queued"

  Cenário: Upload de arquivo com formato não suportado
    Dado que o usuário está autenticado
    E selecionou um arquivo PNG de 200 KB
    Quando o usuário clica no botão de envio
    Então o sistema retorna o código HTTP 400
    E o corpo da resposta contém a mensagem "Formato de arquivo não suportado"

  Cenário: Upload de arquivo excedendo tamanho máximo
    Dado que o usuário está autenticado
    E selecionou um arquivo PDF de 25 MB
    Quando o usuário clica no botão de envio
    Então o sistema retorna o código HTTP 413
    E o corpo da resposta contém a mensagem "Tamanho do arquivo excede o limite de 20 MB"
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-001 | Upload de PDF válido (500 KB) | HTTP 200, UUID retornado, arquivo persistido |
| TEST-002 | Upload de DOCX válido (1 MB) | HTTP 200, UUID retornado, arquivo persistido |
| TEST-003 | Upload de TXT válido (10 KB) | HTTP 200, UUID retornado, arquivo persistido |
| TEST-004 | Upload de PNG (200 KB) | HTTP 400, mensagem de formato inválido |
| TEST-005 | Upload de PDF de 25 MB | HTTP 413, mensagem de tamanho excedido |
| TEST-006 | Upload de PDF de 0 bytes | HTTP 400, mensagem de arquivo vazio |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Capacidade essencial. Sem ingestão, não há processamento. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Nível de abstração adequado. Não impõe design de interface. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Formatos, tamanhos e respostas são especificados numericamente. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui formatos, limites, validação e resposta esperada. |
| **Singular (Singular)** | [x] Sim [ ] Não | Trata exclusivamente da recepção e validação de arquivos. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com FastAPI e bibliotecas padrão. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por testes automatizados com arquivos de teste. |
| **Correct (Correto)** | [x] Sim [ ] Não | Representa a necessidade real do analista jurídico. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- A VPS deve possuir espaço em disco suficiente para armazenar documentos temporários (mínimo 5 GB).
- O sistema depende de bibliotecas de parsing (PyPDF2, python-docx) para processamento posterior.

### Notas e Suposições
- O arquivo PDF não é protegido por senha.
- O arquivo DOCX não possui macros ou conteúdo criptografado.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- Anexo: Arquivos de teste (test_doc_001.pdf, test_doc_002.docx, test_doc_003.txt)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
