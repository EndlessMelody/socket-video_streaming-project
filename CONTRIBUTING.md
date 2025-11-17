# Contributing Guidelines

## Getting Started

Thank you for considering contributing to the Socket Communication System project. This document provides guidelines and instructions for contributing.

## Development Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first
git clone https://github.com/YOUR_USERNAME/socket-video_streaming-project.git
cd socket-video_streaming-project
git remote add upstream https://github.com/EndlessMelody/socket-video_streaming-project.git
```

### 2. Create a Feature Branch

Always create a new branch for your work:

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a new feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions or modifications

### 3. Make Your Changes

- Write clean, readable code
- Follow Python PEP 8 style guidelines
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Commit Guidelines

Write clear, meaningful commit messages:

```bash
git add .
git commit -m "Add brief description of changes"
```

**Commit Message Format:**
```
Type: Brief description (50 chars or less)

More detailed explanation if needed (wrap at 72 chars).
Explain what and why, not how.

- Bullet points are acceptable
- Use present tense: "Add feature" not "Added feature"
- Reference issues: "Fixes #123" or "Closes #456"
```

**Commit Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, missing semicolons, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
```
feat: Add message encryption support

Implement AES-256 encryption for all messages transmitted
between client and server. Add encryption toggle in settings.

Closes #45
```

```
fix: Resolve connection timeout issue

Increase socket timeout from 30s to 60s to prevent
premature disconnections on slow networks.

Fixes #67
```

### 5. Push Your Changes

```bash
git push origin feature/your-feature-name
```

### 6. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill in the PR template with:
   - Description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if applicable)

## Code Standards

### Python Style Guide

Follow PEP 8 guidelines:

```bash
# Install development dependencies
pip install black pylint mypy

# Format code
black server/ client/

# Lint code
pylint server/ client/

# Type checking
mypy server/ client/
```

### Code Quality Requirements

- **Test Coverage:** Minimum 80% for new code
- **Documentation:** All public functions must have docstrings
- **Type Hints:** Use type hints for function signatures
- **No Warnings:** Code must pass linting without warnings

### Example Code Style

```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ExampleClass:
    """Brief description of the class.
    
    Detailed explanation of the class purpose and usage.
    
    Attributes:
        attribute_name: Description of the attribute
    """
    
    def __init__(self, param: str) -> None:
        """Initialize the class.
        
        Args:
            param: Description of parameter
        """
        self.attribute_name = param
    
    def example_method(self, value: int) -> Optional[str]:
        """Brief description of method.
        
        Detailed explanation of what the method does.
        
        Args:
            value: Description of the argument
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When value is negative
        """
        if value < 0:
            raise ValueError("Value must be non-negative")
        
        return str(value)
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_server.py

# Run with coverage
pytest --cov=server --cov=client tests/

# Run with verbose output
pytest tests/ -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Include docstrings for complex tests

**Example Test:**

```python
import pytest
from server.socket_server import SocketServer


def test_server_initialization():
    """Test that server initializes with correct parameters."""
    server = SocketServer(host='127.0.0.1', port=5555)
    
    assert server.host == '127.0.0.1'
    assert server.port == 5555
    assert server.running is False


def test_server_port_validation():
    """Test that invalid port raises ValueError."""
    with pytest.raises(ValueError):
        SocketServer(host='127.0.0.1', port=99999)
```

## Pull Request Process

### Before Submitting

1. **Update your branch:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature-name
   git rebase main
   ```

2. **Run tests:**
   ```bash
   pytest tests/
   ```

3. **Check code quality:**
   ```bash
   black server/ client/
   pylint server/ client/
   ```

4. **Update documentation** if you changed APIs

### PR Review Process

1. Submit your PR with a clear description
2. Address review comments promptly
3. Keep your PR focused (one feature/fix per PR)
4. Be responsive to feedback
5. Update your PR based on review

### PR Approval Requirements

- All tests must pass
- Code coverage must not decrease
- At least one approval from a maintainer
- No merge conflicts
- All review comments addressed

## Project Structure

When adding new files, follow the existing structure:

```
socket-video_streaming-project/
├── server/              # Server-side code
│   ├── __init__.py
│   ├── socket_server.py
│   └── database/
├── client/              # Client-side code
│   ├── __init__.py
│   ├── socket_client.py
│   └── gui/
├── tests/               # Test files
│   ├── test_server.py
│   └── test_client.py
└── docs/                # Documentation
```

## Documentation

### Updating Documentation

- Update relevant `.md` files in `docs/`
- Use clear, concise language
- Include code examples where appropriate
- Keep formatting consistent

### Documentation Standards

- Use Markdown for all documentation
- Include table of contents for long documents
- Use code blocks with language specification
- Add diagrams for complex concepts

## Communication

### Reporting Issues

When reporting bugs, include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs
- Screenshots if applicable

### Feature Requests

When requesting features:
- Describe the problem you're trying to solve
- Explain your proposed solution
- Consider backwards compatibility
- Discuss alternatives you've considered

### Getting Help

- Check existing issues and documentation first
- Ask questions in issue discussions
- Be respectful and patient
- Provide context and details

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or insults
- Publishing others' private information
- Other conduct that would be inappropriate in a professional setting

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

If you have questions about contributing, please open an issue with the "question" label.

---

Thank you for contributing to the Socket Communication System!
