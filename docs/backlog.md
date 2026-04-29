# Backlog Mínimo

## Release 1: Core

- [ ] RF-01: Criar tarefa com título, descrição e prioridade
  - Critérios de aceite:
    - Deve aceitar título e descrição obrigatórios.
    - Deve permitir seleção de prioridade: `baixa`, `média`, `alta`, `crítica`.
    - Deve retornar código HTTP 201 quando a tarefa for criada.

- [ ] RF-02: Listar tarefas
  - Critérios de aceite:
    - Deve retornar lista de tarefas existentes.
    - Deve incluir título, descrição, prioridade e status em cada item.
    - Deve retornar código HTTP 200.

- [ ] RF-03: Atualizar tarefa
  - Critérios de aceite:
    - Deve permitir atualização de título, descrição, prioridade e status.
    - Deve validar campos obrigatórios quando aplicável.
    - Deve retornar código HTTP 200 com dados atualizados.

- [ ] RF-04: Excluir tarefa
  - Critérios de aceite:
    - Deve excluir tarefa pelo identificador.
    - Deve retornar código HTTP 204 em exclusão bem-sucedida.

- [ ] RF-05: Health check
  - Critérios de aceite:
    - Deve fornecer endpoint de status da API.
    - Deve retornar código HTTP 200 e mensagem simples.

## Release 2: Qualidade

- [ ] RT-01: Documentação OpenAPI/Swagger
  - Critérios de aceite:
    - Deve expor documentação automática das rotas.
    - Deve documentar parâmetros de entrada e respostas.

- [ ] RT-02: Validação de dados
  - Critérios de aceite:
    - Deve validar entradas inválidas e retornar erros claros.
    - Deve impedir criação/atualização com prioridade ou status inválidos.

- [ ] RT-03: Testes básicos
  - Critérios de aceite:
    - Deve incluir testes para endpoints principais.
    - Deve garantir criação, leitura, atualização e exclusão de tarefas.

## Release 3: Entrega Final

- [ ] RT-04: Sugestão de priorização por IA
  - Critérios de aceite:
    - Deve sugerir prioridade com base em metadados de tarefas.
    - Deve permitir que o usuário aceite ou sobreponha a sugestão.

- [ ] RT-05: Filtros por prioridade e status
  - Critérios de aceite:
    - Deve permitir filtrar tarefas por prioridade.
    - Deve permitir filtrar tarefas por status.

- [ ] RT-06: Configuração de ambiente local
  - Critérios de aceite:
    - Deve incluir instruções claras para criar e ativar `.venv`.
    - Deve executar a aplicação localmente com `uvicorn`.
