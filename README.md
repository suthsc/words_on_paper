# My Python Project

A Python project with validation, linting, and standard tooling.

## Features

- ✅ Type hints and mypy checking
- 🎨 Code formatting with black
- 🔍 Linting with ruff
- ✔️ Testing with pytest and coverage
- 📝 Pre-commit hooks
- 📦 Modern packaging with pyproject.toml

## Requirements

- Python 3.9 or higher

## Installation

### Development Setup

1. Clone the repository and navigate to the directory:
```bash
cd my-python-project
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the project in development mode with all dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up pre-commit hooks (optional):
```bash
pre-commit install
```

## Development

### Running Tests

Run tests with coverage:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Generate HTML coverage report:
```bash
pytest --cov=my_python_project --cov-report=html
```

### Code Quality

Format code with black:
```bash
black .
```

Lint code with ruff:
```bash
ruff check .
```

Sort imports with isort:
```bash
isort .
```

Type check with mypy:
```bash
mypy my_python_project
```

Run all checks:
```bash
black --check .
ruff check .
mypy my_python_project
pytest
```

## Project Structure

```
my-python-project/
├── my_python_project/           # Main package
│   ├── __init__.py
│   └── main.py
├── tests/                        # Test directory
│   ├── __init__.py
│   └── test_main.py
├── .gitignore                   # Git ignore patterns
├── .pre-commit-config.yaml      # Pre-commit configuration
├── README.md                    # This file
└── pyproject.toml               # Project configuration
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run the test suite and code quality checks
4. Submit a pull request

## License

MIT License - see LICENSE file for details
