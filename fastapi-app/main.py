from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(
    title="FastAPI Application",
    description="Template FastAPI application",
    version="latest"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Welcome to FastAPI Application",
        "version": "latest"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    return {"status": "healthy"}


@app.get("/api/v1/items/{item_id}")
async def read_item(item_id: int):
    """Пример endpoint с параметром"""
    return {"item_id": item_id, "message": f"Item {item_id} retrieved"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)

