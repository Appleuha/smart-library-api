#!/bin/bash
echo "🎯 ФИНАЛЬНАЯ ПРОВЕРКА ПРОЕКТА"
echo "=============================="

echo ""
echo "1. 🧪 Запуск тестов:"
python -m pytest tests/ -v --tb=short
TEST_RESULT=$?

echo ""
echo "2. 🎨 Проверка форматирования:"
echo "   black:"
python -m black --check .
BLACK_RESULT=$?
echo "   isort:"
python -m isort --check-only .
ISORT_RESULT=$?

echo ""
echo "3. 🔍 Проверка линтинга:"
python -m flake8 .
FLAKE8_RESULT=$?

echo ""
echo "4. 🐳 Проверка Docker файлов:"
echo "   Dockerfile: $( [ -f Dockerfile ] && echo "✅ существует" || echo "❌ отсутствует" )"
echo "   .dockerignore: $( [ -f .dockerignore ] && echo "✅ существует" || echo "❌ отсутствует" )"
echo "   docker-compose.yml: $( [ -f docker-compose.yml ] && echo "✅ существует" || echo "❌ отсутствует" )"

echo ""
echo "5. 📚 Проверка обязательных файлов:"
echo "   README.md: $( [ -f README.md ] && echo "✅ существует" || echo "❌ отсутствует" )"
echo "   LICENSE: $( [ -f LICENSE ] && echo "✅ существует" || echo "❌ отсутствует" )"
echo "   requirements.txt: $( [ -f requirements.txt ] && echo "✅ существует" || echo "❌ отсутствует" )"

echo ""
echo "6. 🔧 Проверка Git Hooks:"
echo "   pre-commit: $( [ -f .git/hooks/pre-commit ] && echo "✅ настроен" || echo "❌ не настроен" )"
echo "   pre-push: $( [ -f .git/hooks/pre-push ] && echo "✅ настроен" || echo "❌ не настроен" )"

echo ""
echo "=============================="
if [ $TEST_RESULT -eq 0 ] && [ $BLACK_RESULT -eq 0 ] && [ $ISORT_RESULT -eq 0 ] && [ $FLAKE8_RESULT -eq 0 ]; then
    echo "🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! ПРОЕКТ ГОТОВ!"
else
    echo "⚠️  ЕСТЬ ПРОБЛЕМЫ ДЛЯ ИСПРАВЛЕНИЯ"
    exit 1
fi
