# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-MAINT-002` |
| **Nome** | Substituição do Modelo SLM via Configuração |
| **Tipo** | `Manutenibilidade` |
| **Prioridade** | `Desejável` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve permitir a substituição do modelo de linguagem (SLM) utilizado na extração estruturada e na consulta RAG sem modificação do código-fonte do backend. A substituição deve ser realizada exclusivamente por meio de alteração em arquivo de configuração (ex: .env ou config.yaml), especificando o caminho absoluto do arquivo GGUF do novo modelo. O sistema deve validar, na inicialização, que o arquivo GGUF especificado existe no disco, que possui extensão .gguf e que o tamanho do arquivo está entre 500 MB e 3 GB. Se a validação falhar, o sistema deve registrar o erro no log, manter o modelo anterior carregado e continuar operando. O sistema deve registrar no banco relacional, para cada extração, a versão do modelo utilizado, permitindo auditoria comparativa entre modelos.

### Condições de Aplicação

- Condição 1: O novo arquivo GGUF está presente no disco da VPS.
- Condição 2: O sistema está sendo reinicializado após alteração da configuração.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Administrador |
| **Requisito Pai** | Não aplicável |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-018: Trocar modelo de linguagem |

---

## Justificativa (Rationale)

Modelos de linguagem evoluem rapidamente. A capacidade de substituir o SLM por um modelo mais recente ou mais adequado ao domínio jurídico, sem recompilar ou modificar código, reduz o tempo de manutenção e permite experimentação controlada (A/B testing entre modelos).

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
Funcionalidade: Substituição do modelo SLM via configuração
  Cenário: Substituição válida
    Dado que o arquivo "/models/novo-modelo-3b-Q4.gguf" existe no disco
    E o arquivo possui 1.9 GB
    Quando o administrador altera a configuração para apontar para esse arquivo
    E reinicia o sistema
    Então o sistema carrega o novo modelo na RAM
    E o sistema registra no log "Modelo carregado: novo-modelo-3b-Q4.gguf"
    E as extrações subsequentes registram a versão "novo-modelo-3b-Q4" no banco

  Cenário: Substituição com arquivo inexistente
    Dado que o arquivo "/models/inexistente.gguf" não existe no disco
    Quando o administrador altera a configuração para apontar para esse arquivo
    E reinicia o sistema
    Então o sistema registra no log "Erro: arquivo GGUF não encontrado"
    E o sistema mantém o modelo anterior carregado
    E o sistema continua respondendo a requisições

  Cenário: Substituição com arquivo fora do tamanho permitido
    Dado que o arquivo "/models/modelo-7b-Q4.gguf" possui 4.2 GB
    Quando o administrador altera a configuração para apontar para esse arquivo
    E reinicia o sistema
    Então o sistema registra no log "Erro: arquivo GGUF excede tamanho máximo de 3 GB"
    E o sistema mantém o modelo anterior carregado
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-069 | Substituição por modelo válido (1.9 GB) | Novo modelo carregado, log registrado, versão persistida |
| TEST-070 | Substituição por arquivo inexistente | Erro no log, modelo anterior mantido, sistema operacional |
| TEST-071 | Substituição por arquivo de 4.2 GB | Erro no log, modelo anterior mantido |
| TEST-072 | Substituição por arquivo de 400 MB | Erro no log (abaixo de 500 MB), modelo anterior mantido |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para evolução do produto sem reescrita de código. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica configuração, não impõe formato de arquivo de config. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | .gguf, 500MB-3GB, caminho absoluto, log, versão persistida. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui validação, fallback, log e auditoria. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na substituição de modelo. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com python-dotenv ou PyYAML + llama-cpp-python. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por alteração de configuração e reinicialização. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de manutenibilidade e experimentação. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- O novo modelo deve ser compatível com a API do llama-cpp-python (formato GGUF).
- O tokenizador do novo modelo deve ser utilizado para contagem de tokens na segmentação.
- A versão do modelo é extraída do nome do arquivo GGUF (sem extensão).

### Notas e Suposições
- O limite de 3 GB garante que o modelo cabe na RAM da VPS de 4GB junto com embeddings e backend.
- O limite de 500 MB evita carregamento de arquivos incompletos ou incorretos.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: Documentação llama-cpp-python (carregamento dinâmico de modelo)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
