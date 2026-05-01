# To-do List API

MicroAPI de tarefas em FastAPI com priorizacao assistida por IA (OpenAI) e fallback heuristico local.

## Objetivo

Fornecer uma API interna simples para criar, listar, atualizar e excluir tarefas com suporte a sugestao automatica de prioridade.

## Funcionalidades

- CRUD de tarefas (`POST`, `GET`, `PUT`, `DELETE` em `/tasks`)
- Health check (`GET /`)
- Priorizacao com IA (`priority_mode=auto`)
- Sobrescrita manual da prioridade (`priority_mode=manual`)
- Filtro de listagem por prioridade e status (`GET /tasks?priority=...&status=...`)

## Requisitos

- Python 3.12+
- PowerShell (instrucoes abaixo consideram Windows/PowerShell)

## Setup Local (RT-06)

1. Clone o repositorio e entre na pasta do projeto.
2. Crie o ambiente virtual.
3. Ative o ambiente virtual.
4. Instale dependencias.
5. Configure variaveis de ambiente.
6. Execute API e testes.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env-example .env
```

Edite o `.env` e preencha sua chave:

```env
OPENAI_API_KEY=
```

## Executar API

```powershell
uvicorn app.main:app --reload
```

Acesse:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/`

## Executar Testes

```powershell
python -m pytest
```

## Variaveis de Ambiente

Definidas em `.env-example`:

- `APP_ENV`
- `APP_HOST`
- `APP_PORT`
- `DATABASE_PATH`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `PRIORITY_ADVISOR_TIMEOUT_SECONDS`

## Estrutura

```text
app/
  api/
  models/
  repository/
  services/
  database.py
  main.py
tests/
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

## Licenca

Este projeto esta sob a licenca MIT. Veja o arquivo `LICENSE`.
