#!/bin/bash
# Code formatting and import organization script
# Run this script from the backend directory to format all Python code

echo "🔧 Formatting Python code..."

# Activate virtual environment
source venv/bin/activate

# Sort imports with isort
echo "📦 Organizing imports with isort..."
isort app/ tests/ --diff --check-only
if [ $? -ne 0 ]; then
    echo "⚠️  Import organization needed. Fixing..."
    isort app/ tests/
    echo "✅ Imports organized"
else
    echo "✅ Imports already organized"
fi

# Format code with black
echo "🎨 Formatting code with black..."
black app/ tests/ --check --diff
if [ $? -ne 0 ]; then
    echo "⚠️  Code formatting needed. Fixing..."
    black app/ tests/
    echo "✅ Code formatted"
else
    echo "✅ Code already formatted"
fi

echo "🎉 Code formatting complete!"