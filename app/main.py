import sqlite3
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import books
from app.schemas.response import ErrorCodes, ErrorResponse

# Создаем приложение
app = FastAPI(
    title="Smart Library API",
    version="1.0.0",
    description="REST API для управления библиотекой книг с соблюдением best practices",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    contact={
        "name": "Smart Library Team",
        "url": "https://github.com/your-username/smart-library-api",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
)


# Инициализация базы данных
def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Создаем таблицу книг
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE,
            year INTEGER CHECK(year >= 1000 AND year <= 2100),
            description TEXT,
            is_available BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Создаем индексы для производительности
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_year ON books(year)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_books_available ON books(is_available)"
    )

    conn.commit()
    conn.close()


# Глобальные обработчики ошибок
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            error="Ошибка валидации данных",
            code=ErrorCodes.VALIDATION_ERROR,
            details={"errors": exc.errors()},
        ).dict(),
        media_type="application/json; charset=utf-8",
    )


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    """Обработчик 404 ошибок"""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            success=False,
            error="Ресурс не найден",
            code=ErrorCodes.NOT_FOUND,
            details={"path": request.url.path},
        ).dict(),
        media_type="application/json; charset=utf-8",
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Обработчик общих ошибок"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error="Внутренняя ошибка сервера",
            code=ErrorCodes.INTERNAL_ERROR,
            details={"error": str(exc)},
        ).dict(),
        media_type="application/json; charset=utf-8",
    )


# Подключаем роутеры API v1
app.include_router(books.router, prefix="/api/v1/books", tags=["books"])


# Системные endpoints
@app.get("/")
async def root():
    """Корневой endpoint API"""
    content = {
        "success": True,
        "message": "Добро пожаловать в Smart Library API! 📚",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),  # ← ИСПРАВЛЕНО: добавили .isoformat()
        "endpoints": {
            "documentation": "/docs",
            "api_v1_books": "/api/v1/books",
            "health": "/health",
        },
    }
    # Используем JSONResponse с правильной кодировкой
    return JSONResponse(content=content, media_type="application/json; charset=utf-8")


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения и базы данных"""
    try:
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        # Проверяем что таблица существует
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='books'"
        )
        table_exists = cursor.fetchone()

        if table_exists:
            # Получаем количество книг
            cursor.execute("SELECT COUNT(*) FROM books")
            result = cursor.fetchone()  # Это кортеж, например (5,)
            book_count = result[0] if result else 0
            db_status = "healthy"
        else:
            book_count = 0
            db_status = "healthy (no books table yet)"

        conn.close()

    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        book_count = 0

    content = {
        "success": True,
        "status": "operational",
        "timestamp": datetime.now().isoformat(),  # ← ИСПРАВЛЕНО: добавили .isoformat()
        "services": {"api": "healthy", "database": db_status},
        "metrics": {"total_books": book_count},
    }

    return JSONResponse(content=content, media_type="application/json; charset=utf-8")


# Middleware для добавления заголовков и обработки кодировки
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Добавление security headers ко всем ответам и обработка кодировки"""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-API-Version"] = "1.0"

    # Для Swagger UI не меняем Content-Type и не обрабатываем тело
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]:
        return response

    # Только для JSON ответов добавляем charset
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["Content-Type"] = "application/json; charset=utf-8"

    return response


# Инициализация при запуске
@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    init_db()
    print("=" * 60)
    print("🚀 Smart Library API запущен!")
    print("📚 Версия API: 1.0")
    print("📍 Адрес: http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs")
    print("🔧 OpenAPI спецификация: http://localhost:8000/api/v1/openapi.json")
    print("=" * 60)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
