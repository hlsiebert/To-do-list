"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.api.task_routes import router as task_router

app: FastAPI = FastAPI()
app.include_router(task_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    """Retorna uma resposta basica de status para validar a API."""
    return {"message": "To-do List API esta rodando"}
