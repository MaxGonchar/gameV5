# Backend Development Guide

This directory contains the FastAPI backend for the game application.

## Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Backend

### Development Server
```bash
# Start the FastAPI development server
./start.sh
```

Or manually:
```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`

### Production
```bash
# For production deployment
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the backend is running, you can access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Testing

### Run All Tests
```bash
# Using the test runner script
./run_tests.sh

# Or manually
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest tests/ -v
```

### Run Tests with Coverage
```bash
# Using the test runner script
./run_tests.sh coverage

# Or manually
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test File
```bash
# Test a specific file
python -m pytest tests/test_character.py -v

# With the test runner
./run_tests.sh character  # Runs tests/test_character.py
```

### Run Specific Test Class
```bash
# Run all tests in a specific class
python -m pytest tests/test_character.py::TestCharacterInitialization -v

# Run tests from multiple classes
python -m pytest tests/test_character.py::TestCharacterMemoryMethods tests/test_character.py::TestCharacterDynamicBehavior -v
```

### Run Specific Test Method
```bash
# Run a single test method
python -m pytest tests/test_character.py::TestCharacterInitialization::test_init_with_minimal_data -v

# Run multiple specific methods
python -m pytest tests/test_character.py::TestCharacterMemoryMethods::test_get_memory_with_existing_memory_list tests/test_character.py::TestCharacterMemoryMethods::test_add_item_to_memory_existing_memory -v
```

### Test Options
```bash
# Verbose output with test names
python -m pytest tests/ -v

# Show print statements and verbose output
python -m pytest tests/ -v -s

# Stop on first failure
python -m pytest tests/ -x

# Run tests matching a pattern
python -m pytest tests/ -k "memory" -v

# Run tests with specific markers (if defined)
python -m pytest tests/ -m "unit" -v
```

## Project Structure

```
backend/
├── app/                    # Application code
│   ├── api/               # API routes
│   ├── builders/          # Prompt builders
│   ├── core/              # Configuration
│   ├── dao/               # Data access objects
│   ├── llm/               # LLM integration
│   ├── models/            # Pydantic models
│   ├── objects/           # Domain objects
│   ├── repositories/      # Repository pattern
│   └── services/          # Business logic
├── data/                  # Data files (YAML configs)
├── tests/                 # Test files
├── requirements.txt       # Python dependencies
├── start.sh              # Development server script
└── run_tests.sh          # Test runner script
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Common environment variables:
- API keys for LLM services
- Database configuration
- Debug settings

## Development Workflow

1. **Start the backend**: `./start.sh`
2. **Check API docs**: Visit `http://localhost:8000/docs`
3. **Make changes**: Edit files in the `app/` directory
4. **Run tests**: `./run_tests.sh` or specific test commands
5. **Check coverage**: `./run_tests.sh coverage`

## Troubleshooting

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Test Issues
```bash
# Ensure Python path is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if all dependencies are installed
pip install -r requirements.txt

# Verify test discovery
python -m pytest --collect-only tests/
```

### Import Errors
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Useful Commands

```bash
# Check code style (if linting tools are installed)
flake8 app/
black app/

# Generate requirements.txt
pip freeze > requirements.txt

# Check installed packages
pip list

# Update all packages
pip install --upgrade -r requirements.txt
```