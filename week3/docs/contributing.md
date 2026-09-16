# Contributing

Help improve Recall!

## Getting Started

### 1. Fork & Clone

```bash
git clone <your-fork>
cd <your-fork-directory>/week3
```

### 2. Create Branch

```bash
git checkout -b feature/your-feature
# or
git checkout -b fix/issue-description
```

### 3. Setup Development Environment

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
make install

# Install dev dependencies
python -m pip install pytest pytest-cov black flake8

# Configure provider
test -f .env || cp .env.example .env
# Configure OpenAI or OpenRouter credentials for live mode; rehearsal needs no key.

# Run tests
pytest tests/
```

## Code Style

### Python Formatting

```bash
# Format code
black withdrawal/ tests/ app.py run_demo.py

# Check style
flake8 withdrawal/ tests/ --max-line-length=100

# Run before committing:
black .
flake8 .
```

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Comments

```python
# Good: Explain WHY, not WHAT
# This retries on 429/500 errors because OpenRouter has transient issues
response = client.request(...)

# Bad: Redundant, explains obvious code
# Make a request
response = client.request(...)
```

## Testing

### Run All Tests

```bash
pytest tests/

# With coverage
pytest tests/ --cov=withdrawal --cov-report=html
```

### Write Tests

```python
# tests/test_example.py
import pytest
from withdrawal.core import Engine

def test_consent_workflow():
    """Test full consent workflow."""
    engine = Engine(':memory:')  # Use in-memory DB
    
    # Arrange
    user_id = 'U1'
    
    # Act
    engine.give_consent(user_id, 'D1')
    
    # Assert
    state = engine.consent_status(user_id)
    assert state['state'] == 'granted'
```

### Test Locally Before Submitting

```bash
# Run tests
pytest tests/

# Check style
black --check .
flake8 .

# Manual testing
make start
# Manually test the feature
make stop
```

## Architecture Changes

### Adding a New Service

**File:** `withdrawal/services.py`

```python
PORTS = {
    'documents': 8101,
    'search': 8102,
    'personalization': 8103,
    'your_service': 8104,  # Add
}

# Add Flask app in withdrawal/service_app.py
```

### Adding a New LLM Agent Tool

**File:** `withdrawal/agent.py`

```python
TOOLS = [
    # ... existing tools
    function('your_tool_name', 
             'Description of what tool does',
             {'param1': {'type': 'string'}, ...},
             ['param1', ...])
]
```

Then implement in **`withdrawal/core.py`**:

```python
class Engine:
    def your_tool_name(self, param1, ...):
        """Implementation."""
        return {...}
```

### Changing the Workflow

**File:** `withdrawal/review.py`

The main investigation flow:
```python
def review_plan(engine, clients, user, request_text, on_event=None):
    # 1. Investigator discovers records
    # 2. Scope reviewer checks findings
    # 3. Judge evaluates proposal
    # 4. Return recommendation
```

Modify this function to change the workflow.

## Documentation

### Update README

Edit `README.md` for major changes visible to users.

### Update Docs Site

Edit files in `docs/`:
- `docs/index.md` — Main page
- `docs/getting-started.md` — Setup guide
- `docs/architecture.md` — System design
- `docs/configuration.md` — Configuration
- `docs/troubleshooting.md` — Issues
- `docs/api.md` — API reference

### Docstring Format

```python
def discover_records(self, query: str) -> List[Dict]:
    """
    Discover records matching query.
    
    Args:
        query: Search term (ID, title, service, or kind)
    
    Returns:
        List of record metadata dicts with keys:
        - id: Record ID
        - service: Service name
        - title: Record title
        - version: Record version
    
    Raises:
        BoundaryError: If query fails
    """
```

## Commit Messages

Good format:
```
type(scope): brief description

Optional longer explanation:
- What changed
- Why it changed
- Any side effects

Fixes #123
```

Examples:
```
feat(agent): add new tool for checking record status
fix(core): handle service timeout gracefully
docs(readme): clarify installation steps
test(review): add tests for scope reviewer
```

## Pull Request Checklist

Before submitting:

- [ ] Code follows style guide (`black .` and `flake8 .`)
- [ ] Tests pass (`pytest tests/`)
- [ ] No new warnings
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Related issues linked

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How to test this change

## Related Issues
Fixes #123

## Screenshots (if UI changes)
Add relevant screenshots
```

## Review Process

1. **Code Review** — Reviewer checks code quality
2. **Testing** — Automated tests must pass
3. **CI/CD** — GitHub Actions checks style & tests
4. **Approval** — Needs 1+ approvals
5. **Merge** — Squash merge to main

## Areas for Contribution

### High Priority

- [ ] Better error messages
- [ ] Performance improvements
- [ ] Documentation improvements
- [ ] Test coverage (target: >80%)

### Medium Priority

- [ ] New agent capabilities
- [ ] Support for more LLM providers
- [ ] Better logging
- [ ] Accessibility improvements

### Low Priority

- [ ] UI polish
- [ ] New demo scenarios
- [ ] Example configurations
- [ ] Blog posts / tutorials

## Development Tips

### Quick Iteration

```bash
# Terminal 1: Start services
make start

# Terminal 2: Make code changes
vim withdrawal/agent.py

# Terminal 3: Run tests as you change
pytest tests/ -v --tb=short

# Reload Streamlit manually (F5 in browser)
```

### Debug Mode

```bash
# Add breakpoints
import pdb; pdb.set_trace()

# Or use Python debugger
python -m pdb run_demo.py

# Check logs
make logs
```

### Profile Performance

```python
import time

start = time.time()
# code to measure
elapsed = time.time() - start
print(f"Took {elapsed:.2f}s")
```

## Release Process

1. Update version in `setup.py` (if exists)
2. Update `CHANGELOG.md`
3. Create tag: `git tag v1.2.3`
4. Push: `git push origin v1.2.3`

## Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Help others learn and grow
- Give credit where due

## Questions?

- Check [Contributing Guide](contributing.md) (this page)
- Ask in PR discussions
- File an issue for major changes

---

**Thank you for contributing!** 🎉
