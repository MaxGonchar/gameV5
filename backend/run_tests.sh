#!/bin/bash

# Test runner script for Character class tests
# Usage: ./run_tests.sh [options]

# Change to backend directory
cd "$(dirname "$0")"

echo "Running Character class unit tests..."
echo "======================================="

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run specific tests based on arguments
if [ "$1" = "character" ]; then
    echo "Running Character tests only..."
    python -m pytest tests/test_character.py -v
elif [ "$1" = "coverage" ]; then
    echo "Running tests with coverage report..."
    python -m pytest tests/test_character.py --cov=app.objects.character --cov-report=html --cov-report=term
elif [ "$1" = "verbose" ]; then
    echo "Running tests in verbose mode..."
    python -m pytest tests/test_character.py -v -s
else
    echo "Running all Character tests..."
    python -m pytest tests/test_character.py
fi

echo ""
echo "Tests completed!"