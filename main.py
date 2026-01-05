import string
import random
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

# 1. Инициализация
app = FastAPI(
    title="MicroLink API MVP",
    description="Simple URL Shortener API (In-Memory)",
    version="0.1.0"
)

# 2. Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище в памяти: short_code -> original_url
url_db: Dict[str, str] = {}

# Модели данных
class URLPayload(BaseModel):
    url: HttpUrl

class ShortURLResponse(BaseModel):
    short_code: str
    original_url: HttpUrl

# Вспомогательная функция генерации кода
def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(length))
        if code not in url_db:
            return code

# 3. Эндпоинты

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "MicroLink API is running!",
        "links_count": len(url_db)
    }

@app.post("/api/shorten", response_model=ShortURLResponse, status_code=201)
async def shorten_url(payload: URLPayload):
    """
    Принимает длинный URL, генерирует короткий код и сохраняет в памяти.
    """
    short_code = generate_short_code()
    # Конвертируем HttpUrl в строку для хранения
    url_str = str(payload.url)
    
    url_db[short_code] = url_str
    
    return ShortURLResponse(
        short_code=short_code,
        original_url=payload.url
    )

@app.get("/api/{short_code}")
async def redirect_to_url(short_code: str):
    """
    Ищет код в памяти и редиректит на оригинальный URL.
    """
    original_url = url_db.get(short_code)
    
    if not original_url:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    return RedirectResponse(url=original_url)

# 4. Запуск
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)