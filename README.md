# To-do List API

MicroAPI de tarefas em FastAPI com prioridade assistida por IA e fallback heur�stico local.

## Vis�o Geral

Este projeto implementa um MVP para gest�o interna de tarefas com:

- CRUD completo de tarefas
- Persist�ncia em SQLite
- Camada de servi�o separada da API
- Sugest�o de prioridade via LLM (quando dispon�vel)
- Fallback seguro para heur�stica local

## Funcionalidades do MVP

- Criar tarefa (`POST /tasks`)
- Listar tarefas (`GET /tasks`)
- Buscar tarefa por ID (`GET /tasks/{task_id}`)
- Atualizar tarefa (`PUT /tasks/{task_id}`)
- Excluir tarefa (`DELETE /tasks/{task_id}`)
- Health check (`GET /`)

## Stack T�cnica

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

## Instala��o

1. Clone o reposit�rio.
2. Crie e ative o ambiente virtual.
3. Instale as depend�ncias.

```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install pytest
```

## Execu��o

Suba a API com recarregamento autom�tico:

```bash
uvicorn app.main:app --reload
```

Acesse:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/`

## Testes

Executar toda a su�te:

```bash
pytest -q
```

Executar por arquivo:

```bash
pytest tests/test_task_routes.py -q
pytest tests/test_task_service.py -q
pytest tests/test_priority_advisor.py -q
```

## Troubleshooting

- `ModuleNotFoundError: No module named app`
: execute testes sempre pela raiz do projeto com a `.venv` ativa.

- `HTTP Error 401: Unauthorized`
: chave OpenAI invalida/expirada/revogada. Gere nova chave e atualize `.env`.

- Erros de proxy (`nonnumeric port: 'proxy-port'`)
: remova placeholders de `HTTP_PROXY` e `HTTPS_PROXY` no terminal atual.

- Falha de IA com fallback para prioridade media
: verifique chave, rede e quota da conta OpenAI.

## Arquitetura

A arquitetura segue separa��o por responsabilidades:

- `API` (`app/api/task_routes.py`): entrada HTTP, status codes e tratamento de 404.
- `Service` (`app/services/task_service.py`): regras de neg�cio e orquestra��o.
- `Repository` (`app/repository/task_repository.py`): acesso e persist�ncia de dados em SQLite.
- `Advisor` (`app/services/priority_advisor.py`): sugest�o de prioridade com IA/fallback.
- `Models` (`app/models/tasks.py`): contratos de entrada e sa�da (Pydantic).

Fluxo principal:

`Client -> Routes -> TaskService -> (PriorityAdvisor + TaskRepository) -> SQLite`

## Uso da IA para Prioridade

O `PriorityAdvisor` funciona em dois modos:

1. Com `OPENAI_API_KEY` configurada:
   - tenta chamada ao endpoint de modelo
   - usa timeout curto
   - interpreta retorno para prioridade num�rica
2. Sem chave (ou em caso de falha externa):
   - aplica heur�stica local por palavras-chave
   - mant�m comportamento est�vel sem interromper a API

## Variaveis de Ambiente

Definidas em `.env-example`:

- `APP_ENV`
- `APP_HOST`
- `APP_PORT`
- `DATABASE_PATH`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `PRIORITY_ADVISOR_TIMEOUT_SECONDS`

## Modelo de Dados (resumo)

- `id`: UUID
- `title`: string
- `description`: string
- `priority`: `baixa | media | alta | critica`
- `status`: `pendente | em_andamento | concluida`
- `created_at`, `updated_at`, `due_date`

## Limita��es Atuais

- Sem autentica��o/autoriza��o
- Sem pagina��o/filtros avan�ados
- Sem migra��es formais de banco (al�m da inicializa��o/migra��o b�sica)
- Sem su�te de testes de integra��o com banco externo
- Depend�ncia de heur�stica simples no fallback de prioridade

## Pr�ximos Passos

- Adicionar filtros por prioridade e status nos endpoints
- Implementar pagina��o e ordena��o por query params
- Criar camada de configura��o por ambiente (`dev/test/prod`)
- Adotar migra��es versionadas (ex.: Alembic)
- Expandir testes para cen�rios de valida��o e concorr�ncia
- Incluir observabilidade b�sica (logs estruturados + m�tricas)

## Licenca

Este projeto esta sob a licenca MIT. Veja o arquivo `LICENSE`.