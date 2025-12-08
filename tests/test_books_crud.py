def test_create_book(test_client, sample_book_data):
    """Тест создания книги"""
    response = test_client.post("/api/v1/books/", json=sample_book_data)

    assert response.status_code == 201
    data = response.json()

    assert data["success"] is True
    assert data["data"]["title"] == sample_book_data["title"]
    assert data["data"]["author"] == sample_book_data["author"]
    assert "id" in data["data"]


def test_get_book_by_id(test_client):
    """Тест получения книги по ID"""
    # Сначала создадим книгу
    book_data = {
        "title": "Test Get Book",
        "author": "Test Author",
        "isbn": "1111111111",
        "year": 2023,
        "description": "Test",
        "is_available": True,
    }

    create_response = test_client.post("/api/v1/books/", json=book_data)
    book_id = create_response.json()["data"]["id"]

    # Получаем книгу
    response = test_client.get(f"/api/v1/books/{book_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["id"] == book_id
    assert data["data"]["title"] == book_data["title"]


def test_update_book(test_client):
    """Тест обновления книги"""
    # Сначала создадим книгу
    book_data = {
        "title": "Old Title",
        "author": "Old Author",
        "isbn": "2222222222",
        "year": 2020,
        "description": "Old description",
        "is_available": True,
    }

    create_response = test_client.post("/api/v1/books/", json=book_data)
    book_id = create_response.json()["data"]["id"]

    # Обновляем книгу
    update_data = {"title": "New Title", "author": "New Author", "year": 2024}

    response = test_client.put(f"/api/v1/books/{book_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["title"] == "New Title"
    assert data["data"]["author"] == "New Author"
    assert data["data"]["year"] == 2024
    # Старые поля должны остаться
    assert data["data"]["isbn"] == "2222222222"


def test_delete_book(test_client):
    """Тест удаления книги"""
    # Сначала создадим книгу
    book_data = {
        "title": "Book to Delete",
        "author": "Author",
        "isbn": "3333333333",
        "year": 2023,
        "description": "Will be deleted",
        "is_available": True,
    }

    create_response = test_client.post("/api/v1/books/", json=book_data)
    book_id = create_response.json()["data"]["id"]

    # Удаляем книгу
    response = test_client.delete(f"/api/v1/books/{book_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert f"Книга с ID {book_id} успешно удалена" in data["message"]

    # Проверяем что книга действительно удалена
    get_response = test_client.get(f"/api/v1/books/{book_id}")
    assert get_response.status_code == 404


def test_get_books_with_filters(test_client):
    """Тест фильтрации книг"""
    # Очистим базу перед тестом (если нет автоматической очистки)
    response = test_client.get("/api/v1/books/")
    data = response.json()
    for book in data["data"]:
        test_client.delete(f"/api/v1/books/{book['id']}")

    # Создадим несколько книг для теста фильтрации
    books = [
        {
            "title": "Python Programming",
            "author": "Guido van Rossum",
            "isbn": "4444444444",
            "year": 2020,
            "description": "Python book",
            "is_available": True,
        },
        {
            "title": "Python Advanced",
            "author": "Another Author",
            "isbn": "5555555555",
            "year": 2021,
            "description": "Advanced Python",
            "is_available": False,
        },
        {
            "title": "JavaScript Guide",
            "author": "JS Developer",
            "isbn": "6666666666",
            "year": 2022,
            "description": "JS book",
            "is_available": True,
        },
    ]

    for book in books:
        test_client.post("/api/v1/books/", json=book)

    # Дадим время на создание (если нужно)
    import time

    time.sleep(0.1)

    # Теперь используем параметр search вместо author для поиска по названию ИЛИ автору
    response = test_client.get("/api/v1/books/?search=Python")
    assert response.status_code == 200
    data = response.json()
    # Должны найти книги с "Python" в авторе или названии
    assert len(data["data"]) >= 2  # Две книги с "Python" в названии

    # Тест фильтрации по году
    response = test_client.get("/api/v1/books/?year=2021")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["year"] == 2021
    assert data["data"][0]["title"] == "Python Advanced"

    # Тест фильтрации по доступности
    response = test_client.get("/api/v1/books/?available_only=true")
    assert response.status_code == 200
    data = response.json()
    # Все книги должны быть доступны
    for book in data["data"]:
        assert book["is_available"] is True
    # Должно быть 2 доступные книги
    assert len(data["data"]) == 2


def test_pagination(test_client):
    """Тест пагинации"""
    # Создадим несколько книг
    for i in range(15):
        book_data = {
            "title": f"Book {i}",
            "author": f"Author {i}",
            "isbn": f"77777777{i:02d}",
            "year": 2000 + i,
            "description": f"Description {i}",
            "is_available": True,
        }
        test_client.post("/api/v1/books/", json=book_data)

    # Тест первой страницы
    response = test_client.get("/api/v1/books/?limit=5")
    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]) == 5
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["limit"] == 5
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_prev"] is False

    # Тест второй страницы
    response = test_client.get("/api/v1/books/?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]) == 5
    assert data["pagination"]["page"] == 2

    # Тест запроса за пределами данных
    response = test_client.get("/api/v1/books/?skip=100&limit=10")
    assert response.status_code == 200
    data = response.json()

    assert len(data["data"]) == 0
    assert data["pagination"]["has_next"] is False
