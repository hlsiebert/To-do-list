from fastapi import FastAPI

app: FastAPI = FastAPI()

# Instância principal da aplicação FastAPI.
# Rotas e configurações serão adicionadas a partir deste ponto.

@app.get("/")
async def read_root() -> dict[str, str]:
    """Retorna uma resposta básica de status para validar a API."""
    return {"message": "To-do List API está rodando"}
