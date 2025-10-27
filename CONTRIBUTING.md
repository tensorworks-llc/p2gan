# Contributing to p2gan

Thank you for your interest in contributing to p2gan! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and constructive in all interactions. We welcome contributors of all skill levels.

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Use issue templates when available
3. Provide:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Sample code/markdown if applicable

### Suggesting Features

1. Open an issue with `[Feature Request]` prefix
2. Describe the use case
3. Provide examples if possible

### Contributing Code

#### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/p2gan.git
cd p2gan

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e .[dev]
```

#### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following PEP 8
   - Add type hints where appropriate
   - Include docstrings for new functions/classes

3. **Write/update tests**
   ```bash
   # Run tests locally
   pytest

   # Check coverage
   pytest --cov=ganttproject
   ```

4. **Format and lint code**
   ```bash
   # Format with black
   black src/p2gan/ tests/

   # Check with flake8
   flake8 src/p2gan/ tests/

   # Type checking
   mypy src/p2gan/
   ```

5. **Update documentation**
   - Update README.md if needed
   - Add docstrings to new code
   - Update CHANGELOG.md

6. **Commit with clear message**
   ```bash
   git add .
   git commit -m "feat: add support for custom calendars"
   ```

   Commit message format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

7. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Guidelines

- **One feature per PR** - Keep PRs focused
- **Add tests** - New features need tests
- **Update docs** - Document new functionality
- **Pass CI** - All tests must pass
- **Clean history** - Squash commits if needed

### Testing Guidelines

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=ganttproject --cov-report=html
```

#### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Test edge cases
- Use fixtures for setup

Example test:
```python
def test_task_with_dependencies():
    """Test that task dependencies are correctly handled."""
    task1 = Task(id=0, name="First", start_date=datetime(2025, 1, 1), duration=3)
    task2 = Task(id=1, name="Second", start_date=datetime(2025, 1, 4), duration=2)

    dep = Dependency(task_id=1, depends_on=0, type=DependencyType.FINISH_TO_START)
    task2.dependencies.append(dep)

    assert len(task2.dependencies) == 1
    assert task2.dependencies[0].depends_on == 0
```

### Code Style

#### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 88 (Black default)
- Use descriptive variable names

#### Docstring Format

```python
def calculate_end_date(start_date: datetime, duration: int) -> datetime:
    """
    Calculate end date from start date and duration.

    Args:
        start_date: The starting date
        duration: Number of business days

    Returns:
        The calculated end date

    Example:
        >>> calculate_end_date(datetime(2025, 1, 1), 5)
        datetime(2025, 1, 8)
    """
```

### Project Structure

```
p2gan/
├── src/                  # Source code
│   └── p2gan/            # Main package
│       ├── __init__.py   # Package exports
│       ├── models.py     # Data models
│       ├── parser.py     # Markdown parser
│       ├── generator.py   # XML generator
│       ├── analyzer.py    # Analysis tools
│       └── cli.py         # CLI interface
├── tests/                # Test suite
│   ├── test_models.py    # Model tests
│   ├── test_parser.py    # Parser tests
│   └── test_generator.py # Generator tests
├── docs/                 # Documentation
├── samples/              # Example projects
└── utilities/            # Helper scripts
```

### Areas Needing Contribution

- **Testing**: Increase test coverage
- **Documentation**: Improve examples and guides
- **Features**: See GitHub issues for feature requests
- **Performance**: Optimization for large projects
- **Compatibility**: Test with different GanttProject versions

## Questions?

- Open an issue for questions
- Check existing discussions
- Review the documentation

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for helping make p2gan better!
