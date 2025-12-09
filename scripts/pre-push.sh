#!/bin/bash

echo "Running pre-push checks..."

# 1. Форматирование (на всякий случай)
echo "Formatting with isort..."
python -m isort .

echo "Formatting with black..."
python -m black .

# 2. Линтинг
echo "Running flake8..."
python -m flake8 .

if [ $? -ne 0 ]; then
    echo "Flake8 found errors! Push aborted."
    exit 1
fi

# 3. Запуск тестов
echo "Running tests..."
python -m pytest tests/ -v --tb=short

if [ $? -ne 0 ]; then
    echo "Tests failed! Push aborted."
    exit 1
fi

echo "All pre-push checks passed! Ready to push."
