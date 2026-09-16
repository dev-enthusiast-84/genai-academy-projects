# Contributing to Recall

We welcome contributions! This guide will help you get started.

## Quick Start

```bash
# 1. Fork & clone
git clone <your-fork>
cd week3

# 2. Setup dev environment
pip install -r requirements.txt
pip install litellm pytest black flake8

# 3. Download models
ollama pull phi
ollama pull orca-mini

# 4. Start development
make demo
```

## Development Workflow

### 1. Choose an Area

- **Core Logic** → `withdrawal/`
- **LLM Agents** → `withdrawal/agent.py`
- **Services** → `withdrawal/services.py`
- **UI** → `app.py` (Streamlit)
- **Documentation** → `docs/`
- **Testing** → `tests/`

### 2. Make Your Changes

```bash
# Code formatting
black withdrawal/ tests/ app.py

# Style checking
flake8 withdrawal/ tests/ --max-line-length=100

# Run tests
pytest tests/

# Test manually
make demo
```

### 3. Commit & Push

```bash
# Write clear commit message
git commit -m "type(scope): brief description

Longer explanation if needed.

Fixes #123"

# Types: feat, fix, docs, test, refactor, perf
git push origin feature-branch
```

### 4. Submit Pull Request

- Write clear PR description
- Link related issues
- Ensure tests pass
- Request review from maintainers

## Areas for Contribution

### High Impact

- [ ] Performance improvements
- [ ] Test coverage (target: >80%)
- [ ] Documentation improvements
- [ ] Better error handling

### Medium Impact

- [ ] New agent capabilities
- [ ] Support for more LLM providers
- [ ] Enhanced logging
- [ ] UI/UX improvements

### Lower Priority

- [ ] Demo scenarios
- [ ] Example configurations
- [ ] Blog posts / tutorials

## Code Standards

### Python Style

```python
# Good: Clear and concise
def discover_records(self, query: str) -> List[Dict]:
    """Discover records matching query."""
    results = []
    for record in self.db.catalog:
        if self._matches(record, query):
            results.append(record)
    return results

# Bad: Over-complicated
def discover_records(self, query: str) -> List[Dict]:
    return [r for r in [rec for rec in self.db.catalog if isinstance(rec, dict)] 
            if query in str(r)]
```

### Naming Conventions

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Docstrings

```python
def trace_lineage(self, user_id: str, root_id: str) -> Dict:
    """
    Trace dependencies from root record.
    
    Args:
        user_id: User identifier
        root_id: Root record to trace from
        
    Returns:
        Dict with 'records' and 'edges' keys
        
    Raises:
        BoundaryError: If read fails
    """
```

## Testing

### Run Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_core.py::test_consent_workflow -v

# With coverage
pytest tests/ --cov=withdrawal --cov-report=html
```

### Write Tests

```python
def test_consent_workflow():
    """Test full consent workflow."""
    engine = Engine(':memory:')
    
    # Arrange
    user_id = 'U1'
    
    # Act
    engine.give_consent(user_id, 'D1')
    
    # Assert
    state = engine.consent_status(user_id)
    assert state['state'] == 'granted'
```

## Documentation

### Update Docs

Edit files in `docs/`:
- `docs/index.md` — Main page
- `docs/getting-started.md` — Setup guide
- `docs/architecture.md` — System design
- `docs/configuration.md` — Configuration
- `docs/troubleshooting.md` — Issues
- `docs/api.md` — API reference
- `docs/demo-guide.md` — Demo instructions
- `docs/architecture-diagram.md` — Diagrams

### Root-Level Docs

- `README.md` — Quick start
- `ARCHITECTURE.md` — Architecture overview
- `CONTRIBUTING.md` — This file

### Markdown Style

```markdown
# Heading 1

## Heading 2

### Heading 3

**Bold** and *italic*

- Bullet list
- Another item

1. Numbered list
2. Another item

```python
# Code block
print("example")
```

[Link text](url)
```

## Before Submitting

### Checklist

- [ ] Code follows style guide (`black .`)
- [ ] No style issues (`flake8 .`)
- [ ] All tests pass (`pytest tests/`)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No debug code/print statements
- [ ] Related issues are linked

### Common Mistakes

❌ **Don't**:
- Commit `.env` files with secrets
- Add large binary files
- Commit `__pycache__` or `.runtime/`
- Submit without tests
- Use tabs (use spaces)

✅ **Do**:
- Write clear commit messages
- Include docstrings
- Add tests for new features
- Update documentation
- Reference issue numbers

## Review Process

1. **Automated Checks**: Style, tests, linting
2. **Code Review**: Maintainer feedback
3. **Requested Changes**: Address feedback
4. **Approval**: Ready to merge
5. **Merge**: Squash or rebase

## Release Process

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`

## Getting Help

- **Questions?** → Check [docs/](docs/)
- **Issue?** → File GitHub issue with details
- **Clarification?** → Comment on PR/issue

## Code of Conduct

- Be respectful and inclusive
- Focus on code, not people
- Welcome different perspectives
- Help others learn

---

**Thank you for contributing!** 🎉

Questions? [File an issue](https://github.com/dev-enthusiast-84/genai-academy-projects/issues) or join the discussion.
