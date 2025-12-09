#!/bin/bash

echo "🧹 Running isort..."
isort .

echo "🎨 Running black..."
black .

echo "✅ Formatting complete!"
