# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-SEC-002` |
| **Nome** | Expiração de Token JWT em 24 Horas |
| **Tipo** | `Segurança` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve incluir no payload de cada token JWT emitido na autenticação (REQ-FUNC-011) a claim "exp" (expiration time) com valor de timestamp Unix correspondente a 24 horas após a emissão do token. O sistema deve rejeitar requisições que contenham token JWT com claim "exp" anterior ao timestamp atual do servidor, retornando código HTTP 401 e mensagem "Token expirado". O sistema não deve permitir a revalidação automática de tokens expirados (refresh token). O usuário deve realizar novo login para obter token válido. O sistema deve utilizar a biblioteca python-jose para decodificação e validação da claim "exp".

### Condições de Aplicação

- Condição 1: O token JWT foi emitido pelo sistema.
- Condição 2: A requisição contém token no cabeçalho Authorization.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Administrador |
| **Requisito Pai** | REQ-FUNC-011 |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-017: Controlar sessão de usuário |

---

## Justificativa (Rationale)

Tokens JWT sem expiração ou com expiração longa aumentam a janela de exposição em caso de vazamento. A expiração de 24 horas limita o impacto de um token comprometido, forçando reautenticação diária, que é aceitável para um sistema de uso profissional.

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
Funcionalidade: Expiração de token JWT em 24 horas
  Cenário: Token válido dentro do prazo
    Dado que o token foi emitido há 12 horas
    Quando o usuário envia uma requisição com esse token
    Então o sistema aceita o token
    E a requisição é processada com código HTTP 200

  Cenário: Token expirado após 24 horas
    Dado que o token foi emitido há 25 horas
    Quando o usuário envia uma requisição com esse token
    Então o sistema rejeita o token
    E retorna código HTTP 401
    E a mensagem de erro é "Token expirado"

  Cenário: Token expirado exatamente no limite
    Dado que o token foi emitido há 24 horas e 1 segundo
    Quando o usuário envia uma requisição com esse token
    Então o sistema rejeita o token
    E retorna código HTTP 401
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-065 | Token com 12 horas de idade | Aceito, HTTP 200 |
| TEST-066 | Token com 25 horas de idade | Rejeitado, HTTP 401, "Token expirado" |
| TEST-067 | Token com 24h e 1s de idade | Rejeitado, HTTP 401 |
| TEST-068 | Token sem claim "exp" | Rejeitado, HTTP 401 |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para controle de sessão. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica claim e prazo, não impõe biblioteca. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | 24h, claim "exp", timestamp Unix, HTTP 401. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui emissão, validação, rejeição e mensagem. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente na expiração de token. |
| **Feasible (Factível)** | [x] Sim [ ] Não | python-jose suporta validação de exp nativamente. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por testes com tokens de diferentes idades. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de limitar janela de exposição. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-011 (emissão de token JWT).
- Depende da biblioteca python-jose para validação de claims.
- O relógio do servidor deve estar sincronizado (NTP).

### Notas e Suposições
- Não há mecanismo de refresh token na versão 1.0. O usuário deve fazer login novamente.
- A expiração de 24 horas é contada a partir do timestamp de emissão (iat).

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: RFC 7519 (JSON Web Tokens)
- REF-003: OWASP JWT Security Cheat Sheet

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
