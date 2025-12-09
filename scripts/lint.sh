#!/bin/bash

echo "🔍 Running flake8..."
flake8 .

if [ $? -eq 0 ]; then
    echo "✅ No linting errors found!"
else
    echo "❌ Linting errors found!"
    exit 1
fi
