import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def test_db():
    """Создаем тестовую базу данных"""
    test_db_name = "test_library.db"

    # Удаляем если существует
    if os.path.exists(test_db_name):
        os.remove(test_db_name)

    # Создаем новую
    conn = sqlite3.connect(test_db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE books (
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

    # Создаем индексы
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_year ON books(year)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_books_available ON books(is_available)"
    )

    # Добавляем тестовые данные
    cursor.execute(
        """
        INSERT INTO books (title, author, isbn, year, description, is_available)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        ("Test Book 1", "Test Author 1", "1234567890", 2021, "Test description 1", 1),
    )

    cursor.execute(
        """
        INSERT INTO books (title, author, isbn, year, description, is_available)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        ("Test Book 2", "Test Author 2", "0987654321", 2022, "Test description 2", 0),
    )

    conn.commit()
    conn.close()

    yield test_db_name

    # Удаляем после тестов
    if os.path.exists(test_db_name):
        os.remove(test_db_name)


@pytest.fixture(scope="function")
def test_client(test_db, monkeypatch):
    """Тестовый клиент с подменой БД"""
    # Мокаем только соединение с БД, но оставляем реальные вызовы
    original_connect = sqlite3.connect

    def mock_connect(db_path):
        # Если пытаются подключиться к library.db, подменяем на тестовую
        if db_path == "library.db":
            return original_connect(test_db)
        # Иначе используем оригинальную функцию
        return original_connect(db_path)

    monkeypatch.setattr(sqlite3, "connect", mock_connect)

    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_book_data():
    """Тестовые данные для книги"""
    return {
        "title": "Sample Book",
        "author": "Sample Author",
        "isbn": "9783161484100",
        "year": 2023,
        "description": "Sample description",
        "is_available": True,
    }
