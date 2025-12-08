import sqlite3
from datetime import datetime

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    try:
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        # ПРАВИЛЬНЫЙ способ получить count
        cursor.execute("SELECT COUNT(*) FROM books")
        result = cursor.fetchone()  # Возвращает кортеж, например (5,)
        book_count = result[0] if result else 0

        conn.close()

        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        book_count = 0

    return {
        "success": True,
        "status": "operational",
        "timestamp": datetime.now(),
        "services": {"api": "healthy", "database": db_status},
        "metrics": {"total_books": book_count},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
