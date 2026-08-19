# Especificação de Requisitos de Software (SRS)

> **Norma de referência:** ISO/IEC/IEEE 29148:2018  
> **Projeto:** `NormaExtractor`  
> **Versão:** `1.0`  
> **Data:** `19/08/2026`  
> **Autor:** `Candidato JX Estágio Dev`

---

## Histórico de Revisões

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Rascunho inicial |

---

## 1. Introdução

### 1.1 Propósito (Purpose)

Este documento especifica os requisitos do sistema NormaExtractor, responsável por receber documentos normativos em formato digital, extrair informações estruturadas de forma automatizada, armazenar os dados em banco vetorial e relacional, e permitir consulta interativa ao conteúdo processado por meio de interface web.

### 1.2 Escopo (Scope)

- **a)** Identificação do produto: NormaExtractor, versão 1.0.
- **b)** O produto recebe arquivos PDF, DOCX e TXT contendo textos legais ou normativos, converte o conteúdo em texto plano, segmenta em unidades processáveis, extrai campos estruturados (cláusulas, obrigações, prazos, penalidades), indexa semanticamente e disponibiliza consulta via chat com geração aumentada por recuperação (RAG).
- **c)** Aplicação: ferramenta de apoio a equipes jurídicas, de compliance e de regulamentação que necessitam estruturar e consultar grandes volumes de documentos normativos. Benefícios: redução de tempo de análise manual, padronização de extração, rastreabilidade de fontes.
- **d)** Não há especificação de nível superior (ERS do sistema). Este SRS cobre o produto de software de forma independente.

### 1.3 Referências (References)

| Referência | Título | Versão | Data | Fonte |
|------------|--------|--------|------|-------|
| REF-001 | ISO/IEC/IEEE 29148:2018 | 2018 | 2018 | ISO |
| REF-002 | TEMPLATE_SRS.md | 1.0 | 19/08/2026 | Projeto |
| REF-003 | TEMPLATE_REQUISITO.md | 1.0 | 19/08/2026 | Projeto |

### 1.4 Termos (Terms)

| Termo | Definição |
|-------|-----------|
| Chunk | Segmento de texto contínuo extraído de um documento, delimitado por critérios de tamanho e coerência semântica. |
| Embedding | Representação numérica vetorial de um texto, gerada por modelo de linguagem, que permite comparação semântica. |
| RAG | Retrieval-Augmented Generation. Técnica de consulta em que um modelo de linguagem gera respostas fundamentadas em trechos recuperados de uma base de conhecimento. |
| SLM | Small Language Model. Modelo de linguagem com quantidade reduzida de parâmetros, projetado para execução em hardware com recursos limitados. |
| Documento normativo | Texto legal, regulamentar ou administrativo que estabelece regras, obrigações, direitos ou procedimentos. |
| Extração estruturada | Processo de identificação e extração de campos predefinidos (ex: tipo de cláusula, sujeito, ação, prazo) a partir de texto não estruturado. |
| Coverage | Métrica que indica a proporção de campos esperados que foram extraídos com sucesso em um documento. |

### 1.5 Abreviações (Abbreviations)

| Abreviação | Significado |
|------------|-------------|
| SRS | Software Requirements Specification |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| JSON | JavaScript Object Notation |
| VPS | Virtual Private Server |
| RAM | Random Access Memory |
| CPU | Central Processing Unit |
| GPU | Graphics Processing Unit |
| GGUF | GPT-Generated Unified Format |
| Q4_K_M | Quantização de 4 bits, método K-quant com mistura de tipos |
| UI | User Interface |
| UX | User Experience |
| BDD | Behavior-Driven Development |
| TBD | To Be Defined |

---

## 2. Visão Geral do Produto (Product Overview)

### 2.1 Perspectiva do Produto (Product Perspective)

O NormaExtractor é um sistema autônomo que opera em servidor virtual (VPS) com 4 GB de RAM. Não possui dependência de serviços de nuvem proprietários para inferência de linguagem. O sistema é composto por três elementos principais: interface web (frontend), serviço de processamento (backend) e motor de inferência local (SLM).

#### 2.1.1 Interfaces de Sistema (System Interfaces)

- **Interface de ingestão de arquivos:** O sistema recebe arquivos via protocolo HTTP/HTTPS multipart/form-data. A funcionalidade do software consiste em validar tipo MIME, verificar tamanho máximo e encaminhar para o pipeline de processamento.
- **Interface de consulta RAG:** O sistema recebe mensagens de texto via HTTP/HTTPS JSON e retorna respostas geradas com base em trechos recuperados do banco vetorial.

#### 2.1.2 Interfaces de Usuário (User Interfaces)

- **Interface de upload:** Tela com campo de seleção de arquivo, barra de progresso de upload, lista de documentos processados e indicador de status.
- **Interface de dashboard:** Tela com tabela de documentos, filtros por data, tipo de documento e status de extração. Exibe métricas de coverage e consistência.
- **Interface de chat:** Tela com histórico de mensagens, campo de entrada de texto, indicador de processamento e citação de fontes (trechos do documento que fundamentam a resposta).

#### 2.1.3 Interfaces de Hardware (Hardware Interfaces)

O sistema não possui interfaces de hardware diretas. Opera exclusivamente sobre recursos virtuais da VPS: CPU, RAM, armazenamento em disco e interface de rede.

#### 2.1.4 Interfaces de Software (Software Interfaces)

| Produto | Mnemônico | Especificação | Versão | Fonte |
|---------|-----------|---------------|--------|-------|
| Llama CPP Python | llama-cpp-python | PyPI | 0.2.x | PyPI |
| ChromaDB | chromadb | PyPI | 0.5.x | PyPI |
| LangChain | langchain | PyPI | 0.2.x | PyPI |
| FastAPI | fastapi | PyPI | 0.11x | PyPI |
| React | react | npm | 18.x | npm |
| SQLite | sqlite | Built-in | 3.x | Python |

- **Interface com llama-cpp-python:** O backend invoca o modelo GGUF via bindings Python. A interface consiste em chamadas síncronas ou assíncronas para geração de texto e embeddings.
- **Interface com ChromaDB:** O backend persiste e consulta vetores via API Python embutida. A interface consiste em operações de add, query e get.

#### 2.1.5 Interfaces de Comunicação (Communication Interfaces)

- **Protocolo de rede:** HTTP/1.1 e HTTP/2 sobre TLS 1.2.
- **Formato de mensagens:** JSON para APIs REST, multipart/form-data para upload de arquivos, Server-Sent Events (SSE) para streaming de respostas do chat.

#### 2.1.6 Restrições de Memória (Memory Constraints)

- A memória RAM disponível no ambiente de execução é de 4 GB.
- O modelo de linguagem (SLM) quantizado em Q4_K_M consome aproximadamente 1.8 GB de RAM durante a inferência.
- O modelo de embeddings consome aproximadamente 400 MB de RAM.
- O backend, banco de dados e sistema operacional consomem aproximadamente 1 GB de RAM em operação simultânea.
- O sistema deve operar sem ativar memória de swap durante o processamento de um único documento de até 50 páginas.

#### 2.1.7 Operações (Operations)

- **Modo de operação:** Contínuo, 24 horas por dia, 7 dias por semana.
- **Operação interativa:** Upload de documentos, consulta ao dashboard, interação no chat.
- **Operação não assistida:** Processamento em fila de documentos enviados, geração de embeddings, extração estruturada em batch.
- **Backup:** O banco SQLite e os arquivos de ChromaDB devem ser copiados para diretório de backup diariamente via script agendado (cron).
- **Recuperação:** Em caso de falha do processo do SLM, o backend deve reiniciar o serviço automaticamente em até 30 segundos.

#### 2.1.8 Requisitos de Adaptação de Site (Site Adaptation Requirements)

- Não aplicável. O sistema é executado em ambiente virtualizado padronizado.

#### 2.1.9 Interfaces com Serviços (Interfaces with Services)

- Não há dependência de serviços externos SaaS para inferência. O download do modelo GGUF ocorre uma única vez durante a instalação.

### 2.2 Funções do Produto (Product Functions)

As principais funções do NormaExtractor são:

1. **Ingestão de documentos:** Receber, validar e converter arquivos PDF, DOCX e TXT em texto plano.
2. **Segmentação e indexação:** Dividir o texto em chunks, gerar embeddings e armazenar no banco vetorial.
3. **Extração estruturada:** Identificar e extrair campos predefinidos (tipo de cláusula, sujeito, ação, prazo, base legal, penalidade) de cada chunk.
4. **Armazenamento estruturado:** Persistir extrações validadas em banco relacional com referência ao documento e chunk de origem.
5. **Consulta interativa:** Permitir que o usuário envie perguntas em linguagem natural e receba respostas fundamentadas em trechos dos documentos processados (RAG).
6. **Métricas de qualidade:** Calcular e exibir coverage, consistência e latência de processamento.
7. **Gerenciamento de documentos:** Listar, filtrar, visualizar e excluir documentos processados.

### 2.3 Características do Usuário (User Characteristics)

| Grupo | Características |
|-------|-----------------|
| Analistas jurídicos | Formação em direito, familiaridade com documentos normativos, experiência intermediária com software de escritório. Não possuem expertise técnica em inteligência artificial. |
| Estagiários de compliance | Estudantes de direito ou áreas correlatas, necessitam de orientação estruturada para identificar obrigações em documentos. Requerem interface intuitiva. |
| Desenvolvedores / Administradores | Expertise técnica, responsáveis por implantação, monitoramento e manutenção do sistema. Acessam logs e métricas de desempenho. |

### 2.4 Limitações (Limitations)

- **a) Requisitos regulatórios:** O processamento ocorre localmente na VPS. Nenhum dado de documento é transmitido para serviços de terceiros.
- **b) Limitações de hardware:** Execução restrita a VPS com 4 GB de RAM e CPU virtualizada sem GPU dedicada. Inferência ocorre em CPU.
- **c) Interfaces para outras aplicações:** Não há integração obrigatória com sistemas legados na versão 1.0.
- **d) Operação paralela:** O SLM processa uma requisição de inferência por vez. Requisições concorrentes são enfileiradas.
- **e) Funções de auditoria:** Cada extração estruturada registra timestamp, versão do modelo e identificador do chunk de origem.
- **f) Funções de controle:** Apenas usuários autenticados podem enviar documentos e acessar o chat.
- **g) Requisitos de linguagem de alto nível:** O código-fonte utiliza Python 3.10+ e TypeScript.
- **h) Protocolos de handshake:** TLS 1.2 para comunicação HTTPS.
- **i) Requisitos de qualidade:** Coverage de extração igual ou superior a 85% para documentos com estrutura padrão.
- **j) Criticidade da aplicação:** Baixa criticidade. Falha no processamento de um documento não compromete documentos previamente processados.
- **k) Considerações de segurança:** Senhas de acesso armazenadas com hash bcrypt. Tokens JWT com expiração de 24 horas.
- **l) Considerações físicas/mentais:** Não aplicável.
- **m) Limitações originadas de outros sistemas:** Não aplicável.

### 2.5 Suposições e Dependências (Assumptions and Dependencies)

- **SUP-001:** O sistema operacional da VPS é Linux (Ubuntu 22.04 LTS ou equivalente).
- **SUP-002:** O Python 3.10 ou superior está instalado no ambiente de execução.
- **SUP-003:** O modelo GGUF está disponível no disco da VPS no momento da inicialização.
- **SUP-004:** A VPS possui conectividade de rede para download inicial do modelo e atualizações de dependências.
- **SUP-005:** O usuário possui navegador web compatível com ES2020 (Chrome, Firefox, Edge, Safari).
- **DEP-001:** O sistema depende da biblioteca llama-cpp-python, que por sua vez depende de compiladores C++ para build de wheels.
- **DEP-002:** O sistema depende do ChromaDB em modo embedded, que utiliza SQLite para metadados.

### 2.6 Distribuição de Requisitos (Apportioning of Requirements)

| Função | Elemento de Software | Versão |
|--------|----------------------|--------|
| Ingestão e conversão de arquivos | Backend (FastAPI) | 1.0 |
| Segmentação e embeddings | Backend (LangChain + ChromaDB) | 1.0 |
| Extração estruturada | Backend (SLM + Pydantic) | 1.0 |
| Consulta RAG | Backend (LangChain + SLM) | 1.0 |
| Interface de upload | Frontend (React) | 1.0 |
| Dashboard de métricas | Frontend (React) | 1.0 |
| Chat interativo | Frontend (React + SSE) | 1.0 |
| Autenticação | Backend (FastAPI + JWT) | 1.0 |

Requisitos adiados para versão futura:
- Integração com sistema de gestão documental externo (versão 2.0).
- Suporte a arquivos OCR de imagens escaneadas (versão 2.0).
- Processamento paralelo em múltiplos documentos via fila distribuída (versão 2.0).

### 2.7 Requisitos Especificados (Specified Requirements)

Os requisitos específicos estão documentados na Seção 3 e nas fichas de requisitos individuais (arquivos REQ-XXX-NNN.md). Cada requisito possui identificador único, descrição não ambígua, condições de aplicação, critérios de verificação e rastreabilidade.

---

## 3. Requisitos Específicos (Specific Requirements)

### 3.1 Interfaces Externas (External Interfaces)

#### 3.1.1 Entrada: Upload de Arquivo

| Atributo | Valor |
|----------|-------|
| Nome do item | Arquivo de documento normativo |
| Propósito | Fornecer o documento a ser processado pelo sistema |
| Fonte | Interface web do usuário |
| Faixa válida | Tamanho entre 1 KB e 20 MB |
| Unidades de medida | Bytes |
| Temporização | Requisição HTTP POST síncrona |
| Relacionamentos | Dispara o pipeline de processamento (REQ-FUNC-002) |
| Formatos de dados | multipart/form-data, campo `file` |
| Formatos de comandos | POST /api/v1/documents/upload |
| Itens incluídos | Arquivo binário, tipo MIME, nome original |

#### 3.1.2 Saída: Resposta de Upload

| Atributo | Valor |
|----------|-------|
| Nome do item | Confirmação de recebimento |
| Propósito | Informar ao usuário que o documento foi aceito para processamento |
| Destino | Interface web do usuário |
| Faixa válida | JSON com campos `document_id`, `status`, `message` |
| Unidades de medida | Não aplicável |
| Temporização | Resposta HTTP em até 5 segundos |
| Relacionamentos | Referencia o documento criado no banco |
| Formatos de dados | application/json |
| Itens incluídos | `document_id` (UUID), `status` ("queued"), `message` (string) |

#### 3.1.3 Entrada: Mensagem de Chat

| Atributo | Valor |
|----------|-------|
| Nome do item | Pergunta do usuário |
| Propósito | Consultar informações nos documentos processados |
| Fonte | Interface web do usuário |
| Faixa válida | Texto entre 5 e 500 caracteres |
| Unidades de medida | Caracteres |
| Temporização | Requisição HTTP POST |
| Relacionamentos | Dispara busca vetorial + geração RAG |
| Formatos de dados | application/json, campo `query` |
| Formatos de comandos | POST /api/v1/chat |
| Itens incluídos | `query` (string), `document_ids` (array de UUID, opcional) |

#### 3.1.4 Saída: Resposta de Chat (Streaming)

| Atributo | Valor |
|----------|-------|
| Nome do item | Resposta gerada com fontes |
| Propósito | Fornecer resposta fundamentada em trechos dos documentos |
| Destino | Interface web do usuário |
| Faixa válida | Texto entre 50 e 2000 caracteres |
| Unidades de medida | Caracteres |
| Temporização | Server-Sent Events, primeira token em até 3 segundos, conclusão em até 60 segundos |
| Relacionamentos | Inclui referências aos chunks de origem |
| Formatos de dados | text/event-stream |
| Itens incluídos | `content` (string), `sources` (array de objetos com `chunk_id`, `document_id`, `text_preview`) |

### 3.2 Funções (Functions)

As funções do sistema estão detalhadas nas fichas de requisitos individuais. A seguir, o mapeamento de requisitos funcionais:

| ID | Nome | Descrição Resumida |
|----|------|-------------------|
| REQ-FUNC-001 | Ingestão de Documentos | Receber e validar arquivos PDF, DOCX, TXT |
| REQ-FUNC-002 | Conversão para Texto Plano | Extrair texto mantendo estrutura de parágrafos |
| REQ-FUNC-003 | Segmentação em Chunks | Dividir texto em segmentos com overlap |
| REQ-FUNC-004 | Geração de Embeddings | Criar vetores semânticos para cada chunk |
| REQ-FUNC-005 | Armazenamento Vetorial | Persistir chunks e embeddings no ChromaDB |
| REQ-FUNC-006 | Extração Estruturada | Extrair campos predefinidos de cada chunk via SLM |
| REQ-FUNC-007 | Validação de Extração | Validar extrações contra schema Pydantic |
| REQ-FUNC-008 | Armazenamento Relacional | Persistir extrações validadas em SQLite |
| REQ-FUNC-009 | Consulta RAG | Recuperar chunks relevantes e gerar resposta |
| REQ-FUNC-010 | Dashboard de Métricas | Exibir coverage, consistência e latência |
| REQ-FUNC-011 | Autenticação de Usuário | Controlar acesso via JWT |
| REQ-FUNC-012 | Streaming de Respostas | Enviar resposta do chat em tempo real |

### 3.3 Requisitos de Usabilidade (Usability Requirements)

- **REQ-USAB-001:** O usuário deve concluir o upload de um documento em no máximo 3 interações (selecionar arquivo, clicar em enviar, confirmar).
- **REQ-USAB-002:** O dashboard deve exibir o status de processamento de cada documento com indicador visual (ícone de cor) que permite distinguir entre "pendente", "processando", "concluído" e "erro" sem leitura de texto.
- **REQ-USAB-003:** O chat deve exibir as fontes (trechos de documento) que fundamentam cada resposta em painel colapsável ao lado da mensagem.

### 3.4 Requisitos de Desempenho (Performance Requirements)

- **REQ-PERF-001:** O sistema deve processar um documento de 10 páginas (aproximadamente 5000 palavras) em no máximo 180 segundos, desde o upload até a conclusão da extração estruturada.
- **REQ-PERF-002:** O tempo de resposta do chat (primeiro token) deve ser inferior a 3 segundos para consultas sobre bases com até 100 documentos processados.
- **REQ-PERF-003:** O consumo de RAM durante o processamento de um documento não deve exceder 3.2 GB.
- **REQ-PERF-004:** O sistema deve suportar até 5 usuários simultâneos na interface web sem degradação perceptível do tempo de resposta.

### 3.5 Requisitos Lógicos de Banco de Dados (Logical Database Requirements)

- **REQ-DB-001:** Cada documento deve possuir identificador UUID, nome original, tipo MIME, data de upload, status de processamento e hash SHA-256 do conteúdo.
- **REQ-DB-002:** Cada chunk deve possuir identificador UUID, referência ao documento de origem, número de ordem, texto completo, embedding vetorial (384 dimensões) e metadados de posição (página inicial, página final).
- **REQ-DB-003:** Cada extração estruturada deve possuir identificador UUID, referência ao chunk de origem, campos extraídos (tipo, sujeito, ação, prazo, base_legal, penalidade), timestamp de extração, versão do modelo SLM utilizado e flag de validação.
- **REQ-DB-004:** O banco de dados relacional (SQLite) deve manter integridade referencial entre documentos, chunks e extrações via chaves estrangeiras.
- **REQ-DB-005:** O banco vetorial (ChromaDB) deve permitir busca por similaridade com distância cosseno, retornando os 5 chunks mais relevantes para uma consulta.

### 3.6 Restrições de Design (Design Constraints)

- **REQ-DES-001:** O modelo de linguagem deve ser executado localmente via llama-cpp-python, utilizando arquivo GGUF quantizado em Q4_K_M.
- **REQ-DES-002:** O sistema não deve utilizar GPUs. Toda a inferência ocorre em CPU.
- **REQ-DES-003:** O banco de dados vetorial deve operar em modo embedded (sem servidor externo).
- **REQ-DES-004:** O frontend deve ser implementado como Single Page Application (SPA) em React com TypeScript.

### 3.7 Conformidade com Padrões (Standards Compliance)

- **REQ-STD-001:** Os requisitos deste documento seguem a estrutura e características da ISO/IEC/IEEE 29148:2018.
- **REQ-STD-002:** As APIs REST seguem o padrão OpenAPI 3.0, com documentação automática via FastAPI.
- **REQ-STD-003:** Os testes de aceitação seguem a sintaxe Gherkin para BDD.

### 3.8 Atributos do Sistema de Software (Software System Attributes)

#### 3.8.1 Confiabilidade (Reliability)

- **REQ-REL-001:** O sistema deve recuperar automaticamente de falhas no processo do SLM em no máximo 30 segundos, preservando o estado dos documentos em processamento.
- **REQ-REL-002:** A taxa de falha no processamento de documentos com formato válido e conteúdo textual não deve exceder 5%.

#### 3.8.2 Disponibilidade (Availability)

- **REQ-AVA-001:** O sistema deve estar disponível para recebimento de requisições 99% do tempo em períodos de 30 dias consecutivos, excluindo manutenções programadas com aviso prévio de 24 horas.

#### 3.8.3 Segurança (Security)

- **REQ-SEC-001:** As senhas de usuário devem ser armazenadas com hash bcrypt (custo 12).
- **REQ-SEC-002:** As sessões de usuário devem ser controladas por tokens JWT com expiração de 24 horas.
- **REQ-SEC-003:** O upload de arquivos deve validar o tipo MIME e rejeitar arquivos executáveis (tipos MIME: application/x-executable, application/x-msdownload, etc.).
- **REQ-SEC-004:** O acesso às APIs deve exigir token JWT válido em todas as rotas, exceto `/api/v1/auth/login` e `/api/v1/health`.

#### 3.8.4 Manutenibilidade (Maintainability)

- **REQ-MAINT-001:** O código-fonte do backend deve possuir cobertura de testes unitários igual ou superior a 70%.
- **REQ-MAINT-002:** O pipeline de extração deve permitir substituição do modelo SLM sem modificação do código de negócio, via configuração de caminho do arquivo GGUF.

#### 3.8.5 Portabilidade (Portability)

- **REQ-PORT-001:** O sistema deve ser implantável em VPS Linux com arquitetura x86_64 ou ARM64, utilizando apenas Docker ou docker-compose.
- **REQ-PORT-002:** O frontend deve ser compatível com navegadores Chrome 90+, Firefox 88+, Edge 90+ e Safari 14+.

---

## 4. Verificação (Verification)

| Requisito | Tipo de Teste | Critérios de Aceitação |
|-----------|--------------|------------------------|
| REQ-FUNC-001 | Teste de integração | Upload de PDF, DOCX e TXT aceitos; arquivos inválidos rejeitados com código 400 |
| REQ-FUNC-002 | Teste unitário | Texto extraído de PDF de 10 páginas contém no mínimo 90% das palavras do original |
| REQ-FUNC-003 | Teste unitário | Documento de 5000 palavras gera entre 15 e 30 chunks |
| REQ-FUNC-004 | Teste unitário | Embedding gerado possui 384 dimensões e valores numéricos finitos |
| REQ-FUNC-005 | Teste de integração | Chunk inserido no ChromaDB é recuperado por busca de texto idêntico com score acima de 0.85 |
| REQ-FUNC-006 | Teste de sistema | Documento de teste com 3 cláusulas conhecidas gera extrações com coverage >= 85% |
| REQ-FUNC-007 | Teste unitário | Extração com campo obrigatório ausente é rejeitada pelo schema Pydantic |
| REQ-FUNC-008 | Teste de integração | Extração validada é recuperada do SQLite via API em menos de 1 segundo |
| REQ-FUNC-009 | Teste de sistema | Pergunta sobre documento de teste retorna resposta com fonte correta em 90% dos casos |
| REQ-FUNC-010 | Teste de usabilidade | Dashboard exibe 3 métricas com valores numéricos atualizados em tempo real |
| REQ-FUNC-011 | Teste de segurança | Requisição sem token JWT retorna código 401; requisição com token válido retorna 200 |
| REQ-FUNC-012 | Teste de sistema | Primeiro evento SSE é recebido em menos de 3 segundos após envio da pergunta |
| REQ-PERF-001 | Teste de desempenho | Documento de 10 páginas processado em <= 180 segundos (média de 5 execuções) |
| REQ-PERF-002 | Teste de desempenho | Latência do primeiro token <= 3 segundos (média de 10 consultas) |
| REQ-PERF-003 | Teste de desempenho | Consumo de RAM monitorado via psutil não excede 3.2 GB durante o processamento |
| REQ-SEC-001 | Teste de segurança | Senha "teste123" armazenada no banco não é igual ao texto plano |
| REQ-SEC-002 | Teste de segurança | Token JWT expirado após 24 horas é rejeitado com código 401 |
| REQ-REL-001 | Teste de confiabilidade | Simulação de falha do SLM (SIGKILL) é seguida de reinicialização em <= 30 segundos |

---

## 5. Informações de Suporte (Supporting Information)

- **a)** Exemplos de formatos de entrada: arquivos PDF de leis federais brasileiras, resoluções de órgãos reguladores, contratos administrativos.
- **b)** O projeto inclui um conjunto de 5 documentos de teste (anexos) para validação do pipeline de extração.
- **c)** Problema resolvido: a análise manual de documentos normativos é demorada, inconsistente e não escalável. O NormaExtractor automatiza a estruturação e consulta desses documentos com custo zero de API externa.
- **d)** Empacotamento: o sistema é distribuído como imagens Docker com docker-compose.yml para execução em VPS.

---

## Apêndice A — Índice

- REQ-FUNC-001 a REQ-FUNC-012: Requisitos Funcionais
- REQ-USAB-001 a REQ-USAB-003: Requisitos de Usabilidade
- REQ-PERF-001 a REQ-PERF-004: Requisitos de Performance
- REQ-DB-001 a REQ-DB-005: Requisitos de Banco de Dados
- REQ-DES-001 a REQ-DES-004: Restrições de Design
- REQ-STD-001 a REQ-STD-003: Conformidade com Padrões
- REQ-REL-001 a REQ-REL-002: Confiabilidade
- REQ-AVA-001: Disponibilidade
- REQ-SEC-001 a REQ-SEC-004: Segurança
- REQ-MAINT-001 a REQ-MAINT-002: Manutenibilidade
- REQ-PORT-001 a REQ-PORT-002: Portabilidade

---

## Apêndice B — Modelos de Análise

### Diagrama de Blocos do Sistema

```
+-----------+     HTTP/REST      +-------------------+     Python API     +------------------+
|  React    | <--------------> |   FastAPI         | <--------------> |  llama-cpp-python|
| Frontend  |   (JSON/SSE)     |   Backend         |   (GGUF model)     |  (SLM 3B Q4)     |
+-----------+                  +-------------------+                    +------------------+
                                      |  ^
                                      |  | Python API
                                      v  |
                                +-------------------+
                                |  ChromaDB         |
                                |  (embedded)       |
                                +-------------------+
                                      |  ^
                                      |  | SQLAlchemy
                                      v  |
                                +-------------------+
                                |  SQLite           |
                                |  (relational)     |
                                +-------------------+
```

---

## Apêndice C — Lista de Itens a Definir (TBD)

| ID | Localização | Descrição | Responsável | Prazo |
|----|-------------|-----------|-------------|-------|
| TBD-001 | Seção 2.1.4 | Versão exata do llama-cpp-python a ser fixada | Candidato | 25/08/2026 |
| TBD-002 | Seção 3.4 | Valor exato de latência aceitável para bases > 100 documentos | Candidato | 25/08/2026 |
| TBD-003 | Apêndice B | Diagrama de sequência do pipeline de processamento | Candidato | 25/08/2026 |
