# Ficha de Requisito

> **Norma de referência:** ISO/IEC/IEEE 29148:2018 (Seções 5.2.5 e 5.2.8)

---

## Identificação

| Campo | Valor |
|-------|-------|
| **ID** | `REQ-SEC-001` |
| **Nome** | Armazenamento de Senha com Hash Bcrypt |
| **Tipo** | `Segurança` |
| **Prioridade** | `Essencial` |
| **Status** | `Proposto` |
| **Versão** | `1.0` |

---

## Descrição

### Texto do Requisito

O sistema deve armazenar a senha de cada usuário no banco relacional SQLite utilizando o algoritmo de hash bcrypt com fator de custo (rounds) igual a 12. O sistema n deve armazenar a senha em texto plano, nem em formato reversível (criptografia simétrica ou assimétrica). O sistema deve utilizar a biblioteca passlib para geração e verificação do hash. O hash armazenado deve conter o salt gerado automaticamente e o fator de custo, conforme formato padrão do bcrypt. O sistema deve rejeitar tentativas de cadastro de senha com hash gerado por fator de custo inferior a 12.

### Condições de Aplicação

- Condição 1: O usuário está sendo cadastrado ou alterando sua senha.
- Condição 2: O banco relacional está operacional.

---

## Rastreabilidade

| Campo | Valor |
|-------|-------|
| **Fonte (Source)** | Stakeholder: Desenvolvedor / Administrador |
| **Requisito Pai** | REQ-FUNC-011 |
| **Requisitos Filhos** | Não aplicável |
| **Casos de Uso / Histórias Relacionadas** | UC-016: Cadastrar usuário com segurança |

---

## Justificativa (Rationale)

O armazenamento de senhas em texto plano ou com hash fraco expõe os usuários a vazamento de credenciais em caso de acesso não autorizado ao banco de dados. O bcrypt com custo 12 oferece resistência a ataques de força bruta e rainbow tables, equilibrando segurança e tempo de verificação (~250ms por hash em CPU moderna).

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
Funcionalidade: Armazenamento de senha com hash bcrypt
  Cenário: Cadastro de novo usuário
    Dado que o administrador cadastra um usuário com senha "SenhaSegura123!"
    Quando o sistema persiste o usuário no banco
    Então o campo "password_hash" da tabela de usuários não é igual a "SenhaSegura123!"
    E o campo "password_hash" inicia com o prefixo "$2b$12$"
    E o tamanho do campo "password_hash" é igual a 60 caracteres

  Cenário: Verificação de senha correta
    Dado que o usuário possui hash bcrypt no banco
    Quando o sistema verifica a senha "SenhaSegura123!"
    Então a verificação retorna verdadeiro
    E o tempo de verificação é superior a 100 milissegundos

  Cenário: Verificação de senha incorreta
    Dado que o usuário possui hash bcrypt no banco
    Quando o sistema verifica a senha "SenhaErrada123!"
    Então a verificação retorna falso
```

### Casos de Teste Associados
| ID do Teste | Descrição | Resultado Esperado |
|-------------|-----------|--------------------|
| TEST-061 | Hash de senha no cadastro | Não é texto plano, prefixo $2b$12$, 60 caracteres |
| TEST-062 | Verificação de senha correta | Retorna True, tempo > 100ms |
| TEST-063 | Verificação de senha incorreta | Retorna False |
| TEST-064 | Tentativa de hash com custo 10 | Rejeitado pelo sistema |

---

## Análise de Conformidade com a Norma

| Característica | Atende? | Observações |
|----------------|---------|-------------|
| **Necessary (Necessário)** | [x] Sim [ ] Não | Essencial para proteção de credenciais. |
| **Appropriate (Apropriado)** | [x] Sim [ ] Não | Especifica algoritmo e parâmetro, não impõe biblioteca. |
| **Unambiguous (Não ambíguo)** | [x] Sim [ ] Não | bcrypt, custo 12, formato $2b$12$, 60 caracteres. |
| **Complete (Completo)** | [x] Sim [ ] Não | Inclui geração, verificação e rejeição de hash fraco. |
| **Singular (Singular)** | [x] Sim [ ] Não | Foca exclusivamente no armazenamento de senha. |
| **Feasible (Factível)** | [x] Sim [ ] Não | passlib + bcrypt são bibliotecas padrão em Python. |
| **Verifiable (Verificável)** | [x] Sim [ ] Não | Verificável por inspeção do banco e testes de verificação. |
| **Correct (Correto)** | [x] Sim [ ] Não | Atende à necessidade de segurança de credenciais. |
| **Conforming (Conforme)** | [x] Sim [ ] Não | Segue o template e padrão de escrita aprovado. |

---

## Informações Complementares

### Restrições e Dependências
- Depende do REQ-FUNC-011 (cadastro de usuário funcional).
- Depende da biblioteca passlib com backend bcrypt.

### Notas e Suposições
- O fator de custo 12 equilibra segurança e tempo de verificação (~250ms em CPU moderna).
- O tempo de verificação > 100ms é um indicador de que o hash não é trivial.

### Anexos / Referências
- REF-001: ISO/IEC/IEEE 29148:2018
- REF-002: OWASP Password Storage Cheat Sheet

---

## Histórico de Alterações

| Versão | Data | Autor | Alteração |
|--------|------|-------|-----------|
| 1.0 | 19/08/2026 | Candidato JX Estágio Dev | Criação inicial |
