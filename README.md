# To-do List API

Uma micro-API para gestão de tarefas com priorização assistida por IA. Projeto leve para organizar tarefas, definir prioridades e suportar integração rápida com clientes e automações.

## Objetivo

- Fornecer uma API simples para criar, atualizar, listar e remover tarefas.
- Aplicar priorização inteligente para ajudar na organização de atividades mais importantes.
- Servir como base para evolução em direção a workflows colaborativos, dashboards e alertas.

## Stack

- Python 3.x
- FastAPI
- Uvicorn
- Pydantic
- SQLite (ou outra base leve para protótipos)
- Git

## Como rodar localmente

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd To-do-list
   ```

2. Crie o ambiente virtual ou ative o existente:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:
   ```bash
   pip install fastapi uvicorn
   ```

4. Inicie a aplicação:
   ```bash
   uvicorn main:app --reload
   ```

5. Abra o navegador em:
   ```
   http://127.0.0.1:8000/docs
   ```

## Roadmap de releases

### MVP

- CRUD de tarefas
- Definição de prioridade
- Endpoints REST básicos
- Documentação automática via Swagger UI

### Próximas entregas

- Persistência de dados com SQLite ou PostgreSQL
- Filtro por prioridade e status
- Ordenação inteligente de tarefas
- Autenticação básica

### Visão de médio prazo

- Integração com assistente de IA para sugerir prioridades
- Painel de tarefas por usuário e por categoria
- Notificações e lembretes
- API pública para consumo por clientes web e mobile

## Observações

- Este repositório é voltado para prototipagem rápida e evolução incremental.
- Mantenha o ambiente virtual isolado e não versionar dependências diretas no projeto.
