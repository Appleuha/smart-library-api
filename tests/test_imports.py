import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_all_imports():
    """Тест всех импортов"""
    imports = [
        ("fastapi", "FastAPI"),
        ("pydantic", "BaseModel"),
        ("pytest", "__version__"),
        ("sqlite3", "connect"),
        ("app.schemas.book", "BookCreate"),
        ("app.schemas.response", "BookListResponse"),
    ]

    for module_name, attr_name in imports:
        try:
            if module_name.startswith("app."):
                # Динамический импорт для app модулей
                module = __import__(module_name, fromlist=[attr_name])
            else:
                module = __import__(module_name)

            if attr_name != "__version__":
                getattr(module, attr_name)

            print(f"✅ {module_name}.{attr_name}")
        except (ImportError, AttributeError) as e:
            print(f"❌ {module_name}.{attr_name}: {e}")
            return False

    return True


def test_simple():
    assert 1 + 1 == 2
