# To-do List API

MicroAPI de tarefas em FastAPI com prioridade assistida por IA e fallback heurístico local.

## Visão Geral

Este projeto implementa um MVP para gestão interna de tarefas com:

- CRUD completo de tarefas
- Persistência em SQLite
- Camada de serviço separada da API
- Sugestão de prioridade via LLM (quando disponível)
- Fallback seguro para heurística local

## Funcionalidades do MVP

- Criar tarefa (`POST /tasks`)
- Listar tarefas (`GET /tasks`)
- Buscar tarefa por ID (`GET /tasks/{task_id}`)
- Atualizar tarefa (`PUT /tasks/{task_id}`)
- Excluir tarefa (`DELETE /tasks/{task_id}`)
- Health check (`GET /`)

## Stack Técnica

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLite
- Uvicorn
- Pytest

## Estrutura do Projeto

```text
app/
  api/
    task_routes.py
  models/
    tasks.py
  repository/
    task_repository.py
  services/
    task_service.py
    priority_advisor.py
  database.py
  main.py
tests/
  test_task_routes.py
  test_task_service.py
  test_priority_advisor.py
```

## Instalação

1. Clone o repositório.
2. Crie e ative o ambiente virtual.
3. Instale as dependências.

```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest
```

## Execução

Suba a API com recarregamento automático:

```bash
uvicorn app.main:app --reload
```

Acesse:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/`

## Testes

Executar toda a suíte:

```bash
pytest -q
```

Executar por arquivo:

```bash
pytest tests/test_task_routes.py -q
pytest tests/test_task_service.py -q
pytest tests/test_priority_advisor.py -q
```

## Arquitetura

A arquitetura segue separação por responsabilidades:

- `API` (`app/api/task_routes.py`): entrada HTTP, status codes e tratamento de 404.
- `Service` (`app/services/task_service.py`): regras de negócio e orquestração.
- `Repository` (`app/repository/task_repository.py`): acesso e persistência de dados em SQLite.
- `Advisor` (`app/services/priority_advisor.py`): sugestão de prioridade com IA/fallback.
- `Models` (`app/models/tasks.py`): contratos de entrada e saída (Pydantic).

Fluxo principal:

`Client -> Routes -> TaskService -> (PriorityAdvisor + TaskRepository) -> SQLite`

## Uso da IA para Prioridade

O `PriorityAdvisor` funciona em dois modos:

1. Com `OPENAI_API_KEY` configurada:
   - tenta chamada ao endpoint de modelo
   - usa timeout curto
   - interpreta retorno para prioridade numérica
2. Sem chave (ou em caso de falha externa):
   - aplica heurística local por palavras-chave
   - mantém comportamento estável sem interromper a API

### Configuração opcional da chave

PowerShell:

```powershell
$env:OPENAI_API_KEY = "sua_chave"
```

## Modelo de Dados (resumo)

- `id`: UUID
- `title`: string
- `description`: string
- `priority`: `baixa | media | alta | critica`
- `status`: `pendente | em_andamento | concluida`
- `created_at`, `updated_at`, `due_date`

## Limitações Atuais

- Sem autenticação/autorização
- Sem paginação/filtros avançados
- Sem migrações formais de banco (além da inicialização/migração básica)
- Sem suíte de testes de integração com banco externo
- Dependência de heurística simples no fallback de prioridade

## Próximos Passos

- Adicionar filtros por prioridade e status nos endpoints
- Implementar paginação e ordenação por query params
- Criar camada de configuração por ambiente (`dev/test/prod`)
- Adotar migrações versionadas (ex.: Alembic)
- Expandir testes para cenários de validação e concorrência
- Incluir observabilidade básica (logs estruturados + métricas)
