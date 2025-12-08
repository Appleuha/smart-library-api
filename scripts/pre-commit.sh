#!/bin/bash

echo "🔍 Running pre-commit checks..."

# 1. Форматирование
echo "🧹 Formatting with isort..."
python -m isort .

echo "🎨 Formatting with black..."
python -m black .

# 2. Линтинг
echo "🔍 Running flake8..."
python -m flake8 .

if [ $? -ne 0 ]; then
    echo "❌ Flake8 found errors! Commit aborted."
    exit 1
fi

echo "✅ Pre-commit checks passed! Ready to commit."