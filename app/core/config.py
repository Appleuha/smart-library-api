import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Основные настройки
    APP_NAME: str = os.getenv("APP_NAME", "Smart Library API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./library.db")

    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")

    # Пагинация
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "100"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "1000"))

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_DESCRIPTION: str = """
    Smart Library API - современный REST API для управления библиотекой книг.
    ## Возможности
    * **CRUD операции** с книгами
    * **Пагинация и фильтрация**
    * **Поиск** по книгам
    * **Валидация данных**
    * **Полная документация** (Swagger/ReDoc)
    ## Версионирование
    Текущая версия API: **v1**
    """

    class Config:
        env_file = ".env"


settings = Settings()
