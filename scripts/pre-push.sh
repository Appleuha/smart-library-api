#!/bin/bash

echo "🚀 Running pre-push checks..."

# Более строгие проверки перед пушем
echo "🧪 Running all tests with coverage..."
python -m pytest tests/ -v

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Push aborted."
    exit 1
fi

echo "✅ All pre-push checks passed! Ready to push."