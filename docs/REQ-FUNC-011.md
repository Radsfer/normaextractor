# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-FUNC-011` |
| **Nome** | Autenticação de Usuário via JWT |
| **Tipo** | `Funcional` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve autenticar usuários por meio de nome de usuário (email) e senha. A senha deve conter no mínimo 8 caracteres, incluindo pelo menos 1 letra maiúscula, 1 letra minúscula, 1 número e 1 caractere especial. O sistema deve armazenar a senha com hash bcrypt (custo 12). Após autenticação bem-sucedida, o sistema deve emitir um token JWT com expiração de 24 horas. O sistema deve rejeitar requisições às APIs protegidas (upload, chat, dashboard, listagem de documentos) que não contenham token JWT válido no cabeçalho Authorization, retornando código HTTP 401. As rotas públicas (/api/v1/auth/login, /api/v1/health) não exigem token. O sistema deve permitir que o usuário encerre a sessão explicitamente, invalidando o token no lado cliente.

### Condições de Aplicação

- Condição 1: O usuário possui cadastro prévio no sistema.
- Condição 2: O banco relacional contém o registro do usuário com hash de senha.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Administrador |
| **Requisito Pai** | Não aplicável |
| **Requisitos Filhos** | REQ-SEC-001, REQ-SEC-002 |
| **Casos de Uso / Histórias Relacionadas** | UC-011: Autenticar no sistema |

---

## Justificativa (Rationale)

O sistema processa documentos que podem conter informações sensíveis ou restritas. A autenticação garante que apenas usuários autorizados acessem o conteúdo processado e evite exposição não intencional de dados normativos.

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
Funcionalidade: Autenticação de usuário via JWT
  Cenário: Login com credenciais válidas
    Dado que o usuário possui email "usuario@exemplo.com" e senha "Senha123!"
    E a senha está armazenada com hash bcrypt no banco
    Quando o usuário envia as credenciais para /api/v1/auth/login
    Então o sistema retorna código HTTP 200
    E o corpo da resposta contém um token JWT
    E o token possui expiração de 24 horas

  Cenário: Login com senha incorreta
    Dado que o usuário envia senha "SenhaErrada123!"
    Quando o sistema valida as credenciais
    Então o sistema retorna código HTTP 401
    E a mensagem de erro não revela se o email existe no sistema

  Cenário: Acesso a API protegida sem token
    Dado que o usuário não enviou token JWT
    Quando o usuário requisita /api/v1/documents/upload
    Então o sistema retorna código HTTP 401
    E a mensagem de erro indica "Autenticação necessária"

  Cenário: Acesso a API protegida com token expirado
    Dado que o usuário envia um token JWT com expiração no passado
    Quando o usuário requisita /api/v1/documents/upload
    Então o sistema retorna código HTTP 401
    E a mensagem de erro indica "Token expirado"
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-043 | Login com credenciais válidas | HTTP 200, token JWT com expiração 24h |
| TEST-044 | Login com senha incorreta | HTTP 401, mensagem genérica |
| TEST-045 | Acesso sem token | HTTP 401, "Autenticação necessária" |
| TEST-046 | Acesso com token expirado | HTTP 401, "Token expirado" |
| TEST-047 | Acesso a rota pública sem token | HTTP 200 (health check) |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para proteção de dados. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica mecanismo, mas não impõe biblioteca específica. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | Regras de senha, bcrypt custo 12, 24h, rotas protegidas são claras. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui validação, emissão, expiração, proteção de rotas e logout. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na autenticação. |
| **Feasible (Factível)** | [x] Sim [ ] Não | Implementável com FastAPI + python-jose + passlib. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por testes de login e acesso a rotas. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de controle de acesso. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do banco relacional SQLite para armazenamento de usuários.
- Depende da biblioteca passlib para hash bcrypt.
- Depende da biblioteca python-jose para geração e validação de JWT.

### Notas e Suposições
- O sistema possui um usuário administrador pré-cadastrado na instalação.
- O registro de novos usuários é realizado pelo administrador (não há auto-cadastro na v1.0).

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: RFC 7519 (JSON Web Tokens)

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Rafael Adolfo Silva Ferreira | Criação inicial |
