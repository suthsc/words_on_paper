# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

This is a Python 3.9+ project managed with setuptools. The project uses `uv` for building as indicated by recent commits.

### Common Development Commands

**Setup:**
```bash
# Create and activate virtual environment
uv venv                          # Create virtual environment
source .venv/bin/activate        # Activate it

# Install in development mode with all dependencies
uv pip install -e ".[dev]"       # Install with dependencies

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

**Testing:**
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_main.py

# Run tests with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=my_python_project --cov-report=html
```

**Code Quality:**
```bash
# Format code with black
black .

# Lint with ruff
ruff check .

# Fix ruff issues automatically
ruff check --fix .

# Sort imports with isort
isort .

# Type check with mypy
mypy my_python_project
```

**Run all checks (pre-commit style):**
```bash
black --check .
ruff check .
mypy my_python_project
pytest
```

## Project Architecture

The project follows a standard Python package structure:

- **my_python_project/**: Main package containing the application code
  - **main.py**: Core module with business logic (currently contains a simple `hello_world` function)
  - **__init__.py**: Package initialization that exports the public API

- **tests/**: Unit tests mirror the package structure with `test_*.py` files
  - Tests are discovered and run by pytest automatically
  - Coverage is configured to measure branch coverage by default

## Code Quality Standards

The project is configured with strict linting and type checking:

- **Black**: Code formatter with 88-character line length
- **Ruff**: Linter enforcing PEP 8, import sorting, comprehension style, and bug detection
- **mypy**: Type checker with `check_untyped_defs` enabled (strict type checking for untyped code)
- **pytest**: Testing framework with automatic coverage reporting

Pre-commit hooks run Black, Ruff (with --fix), and mypy before each commit. This ensures code quality is maintained across all commits.

## Testing Configuration

Pytest is configured with automatic coverage reporting:
- Test discovery: Files matching `test_*.py` with classes `Test*` and functions `test_*`
- Coverage reports: HTML report + terminal report with missing line details
- Coverage includes branch coverage for better metrics
- Tests in `tests/` directory are excluded from coverage calculations

Run `pytest --help` for additional options like `-k` for filtering tests by name pattern.
