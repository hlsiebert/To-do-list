"""FastAPI application entrypoint."""

from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.task_routes import router as task_router

load_dotenv()

app: FastAPI = FastAPI(
    title="To-do List API",
    description=(
        "MicroAPI para gestao de tarefas com priorizacao assistida por IA "
        "e fallback heuristico local."
    ),
    version="1.0.0",
    contact={"name": "Equipe Interna"},
)
app.include_router(task_router)


@app.get(
    "/",
    tags=["health"],
    summary="Health check",
    description="Verifica disponibilidade da API.",
)
async def read_root() -> dict[str, str]:
    """Retorna uma resposta basica de status para validar a API."""
    return {"message": "To-do List API esta rodando"}
