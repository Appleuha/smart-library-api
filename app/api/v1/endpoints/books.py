# app/api/v1/endpoints/books.py
import sqlite3
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.schemas.book import BookCreate, BookUpdate
from app.schemas.response import BookListResponse

router = APIRouter()


def get_db_connection():
    """Получение соединения с БД"""
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/", response_model=BookListResponse)
async def get_books(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(
        100, ge=1, le=1000, description="Количество записей на странице"
    ),
    author: Optional[str] = Query(None, description="Фильтр по автору (частичное совпадение)"),
    title: Optional[str] = Query(None, description="Фильтр по названию (частичное совпадение)"),
    year: Optional[int] = Query(None, ge=1000, le=2100, description="Фильтр по году"),
    search: Optional[str] = Query(None, description="Поиск по названию ИЛИ автору"),  # НОВЫЙ параметр
    available_only: bool = Query(False, description="Только доступные книги"),
):
    """Получить список книг с пагинацией и фильтрацией"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Строим запрос
        query = "SELECT * FROM books WHERE 1=1"
        count_query = "SELECT COUNT(*) as total FROM books WHERE 1=1"
        params = []

        if author:
            query += " AND author LIKE ?"
            count_query += " AND author LIKE ?"
            params.append(f"%{author}%")

        if title:
            query += " AND title LIKE ?"
            count_query += " AND title LIKE ?"
            params.append(f"%{title}%")

        if search:  # Поиск по названию ИЛИ автору
            query += " AND (title LIKE ? OR author LIKE ?)"
            count_query += " AND (title LIKE ? OR author LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")

        if year:
            query += " AND year = ?"
            count_query += " AND year = ?"
            params.append(year)

        if available_only:
            query += " AND is_available = 1"
            count_query += " AND is_available = 1"

        # Получаем общее количество
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"]

        # Добавляем пагинацию
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        # Выполняем основной запрос
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Преобразуем Row в dict (правильный способ)
        books = []
        for row in rows:
            book_dict = {}
            for key in row.keys():
                value = row[key]
                # Преобразуем булевы значения
                if key == 'is_available':
                    value = bool(value)
                book_dict[key] = value
            books.append(book_dict)

        conn.close()

        # Рассчитываем пагинацию
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        # Формируем ответ
        response_data = {
            "success": True,
            "data": books,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": skip + limit < total,
                "has_prev": skip > 0,
                "next_page": skip + limit if skip + limit < total else None,
                "prev_page": skip - limit if skip > 0 else None,
            },
            "timestamp": datetime.now().isoformat(),
        }

        return JSONResponse(
            content=response_data, media_type="application/json; charset=utf-8"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении книг: {str(e)}",
        )


@router.get("/{book_id}")
async def get_book(book_id: int):
    """Получить книгу по ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()  # Исправлено: было book, теперь row

        conn.close()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Книга с ID {book_id} не найдена",
            )

        # Преобразуем Row в dict
        book_dict = {}
        for key in row.keys():
            value = row[key]
            if key == 'is_available':
                value = bool(value)
            book_dict[key] = value

        response_data = {
            "success": True,
            "data": book_dict,
            "timestamp": datetime.now().isoformat(),
        }

        return JSONResponse(
            content=response_data, media_type="application/json; charset=utf-8"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении книги: {str(e)}",
        )


@router.post("/", status_code=201)  # Исправлено: явно указываем 201
async def create_book(book: BookCreate):
    """Создать новую книгу"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Вставляем книгу
        cursor.execute(
            """
            INSERT INTO books (title, author, isbn, year, description, is_available)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                book.title,
                book.author,
                book.isbn,
                book.year,
                book.description,
                1 if book.is_available else 0,
            ),
        )

        book_id = cursor.lastrowid

        # Получаем созданную книгу
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()

        conn.commit()
        conn.close()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании книги",
            )

        # Преобразуем Row в dict
        book_dict = {}
        for key in row.keys():
            value = row[key]
            if key == 'is_available':
                value = bool(value)
            book_dict[key] = value

        response_data = {
            "success": True,
            "data": book_dict,
            "message": "Книга успешно создана",
            "timestamp": datetime.now().isoformat(),
        }

        return JSONResponse(
            status_code=201,  # Явно указываем статус код в ответе
            content=response_data, 
            media_type="application/json; charset=utf-8"
        )

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Книга с таким ISBN уже существует",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка базы данных: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании книги: {str(e)}",
        )

@router.put("/{book_id}")
async def update_book(book_id: int, book_update: BookUpdate):
    """Обновить книгу по ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверяем существует ли книга
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        existing_book = cursor.fetchone()
        
        if not existing_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Книга с ID {book_id} не найдена"
            )
        
        # Собираем поля для обновления
        update_fields = []
        update_values = []
        
        if book_update.title is not None:
            update_fields.append("title = ?")
            update_values.append(book_update.title)
        
        if book_update.author is not None:
            update_fields.append("author = ?")
            update_values.append(book_update.author)
        
        if book_update.isbn is not None:
            update_fields.append("isbn = ?")
            update_values.append(book_update.isbn)
        
        if book_update.year is not None:
            update_fields.append("year = ?")
            update_values.append(book_update.year)
        
        if book_update.description is not None:
            update_fields.append("description = ?")
            update_values.append(book_update.description)
        
        if book_update.is_available is not None:
            update_fields.append("is_available = ?")
            update_values.append(1 if book_update.is_available else 0)
        
        # Добавляем updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )
        
        # Добавляем ID в конец значений
        update_values.append(book_id)
        
        # Выполняем обновление
        update_query = f"UPDATE books SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(update_query, update_values)
        
        # Получаем обновленную книгу
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        updated_book = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        response_data = {
            "success": True,
            "data": dict(updated_book),
            "message": "Книга успешно обновлена",
            "timestamp": datetime.now().isoformat(),
        }
        
        return JSONResponse(
            content=response_data,
            media_type="application/json; charset=utf-8"
        )
        
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Книга с таким ISBN уже существует"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка базы данных: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении книги: {str(e)}"
        )


@router.delete("/{book_id}")
async def delete_book(book_id: int):
    """Удалить книгу по ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверяем существует ли книга
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Книга с ID {book_id} не найдена"
            )
        
        # Удаляем книгу
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        
        conn.commit()
        conn.close()
        
        response_data = {
            "success": True,
            "message": f"Книга с ID {book_id} успешно удалена",
            "deleted_book": dict(book),
            "timestamp": datetime.now().isoformat(),
        }
        
        return JSONResponse(
            content=response_data,
            media_type="application/json; charset=utf-8"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении книги: {str(e)}"
        )


@router.patch("/{book_id}")
async def partial_update_book(book_id: int, book_update: BookUpdate):
    """Частично обновить книгу по ID (аналог PUT)"""
    # Используем ту же логику что и PUT
    return await update_book(book_id, book_update)
