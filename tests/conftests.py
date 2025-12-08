# tests/conftest.py
import os
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function")  # Для каждого теста отдельно
def test_client():
    """Создает тестового клиента"""
    # Удаляем старую тестовую базу, если есть
    if os.path.exists("test_library.db"):
        os.remove("test_library.db")

    # Создаем новую базу для тестов
    conn = sqlite3.connect("test_library.db")
    cursor = conn.cursor()

    # Создаем таблицу книг
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

    conn.commit()
    conn.close()

    # Патчим приложение на использование тестовой базы
    import app.api.v1.endpoints.books as books_module

    # Сохраняем оригинальную функцию
    original_get_db_connection = books_module.get_db_connection

    # Создаем новую функцию для тестов
    def test_get_db_connection():
        """Получение соединения с тестовой БД"""
        conn = sqlite3.connect("test_library.db")
        conn.row_factory = sqlite3.Row
        return conn

    # Подменяем функцию
    books_module.get_db_connection = test_get_db_connection

    # Создаем клиент
    client = TestClient(app)

    yield client  # Отдаем клиент тесту

    # После теста восстанавливаем оригинальную функцию
    books_module.get_db_connection = original_get_db_connection

    # Очищаем тестовую базу
    if os.path.exists("test_library.db"):
        os.remove("test_library.db")


@pytest.fixture
def sample_book_data():
    """Фикстура с тестовыми данными книги"""
    return {
        "title": "Test Book",
        "author": "Sample Author",
        "isbn": "9783161484100",
        "year": 2023,
        "description": "Sample description",
        "is_available": True,
    }
