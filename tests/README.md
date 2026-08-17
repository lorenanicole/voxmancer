# Voxmancer Test Suite

Tests are organized by type and scope for clarity and fast feedback loops.

## Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests for individual components with mocked dependencies.

- `test_voice_registry.py` - Voice registry API (list, filter, download URLs)
- `test_voice_mapper_llm.py` - LLM-based voice mapping (with mocked LLM responses)
- `test_voice_mapper.py` - Voice prompt analysis
- `test_models.py` - Pydantic data model validation
- `test_config.py` - Settings and configuration loading

**Run unit tests:**
```bash
poetry run pytest tests/unit/ -v
```

### Integration Tests (`tests/integration/`)

Test subsystems and components working together. May require external services.

- `test_piper_backend.py` - Piper TTS client, voice downloads, config generation
- `test_voice_pipeline.py` - LLM mapper + registry working together

**Run integration tests:**
```bash
poetry run pytest tests/integration/ -v
```

### End-to-End Tests (`tests/e2e/`)

Full CLI workflows testing the complete system. Slow and require all dependencies.

- `test_cli_workflow.py` - `voxmancer workflow --demo` command
- (Future: `test_cli_render.py`, `test_cli_preview.py`)

**Run E2E tests:**
```bash
poetry run pytest tests/e2e/ -v -m e2e
```

## Running Tests

**All tests:**
```bash
poetry run pytest tests/ -v
```

**Only fast tests (skip E2E):**
```bash
poetry run pytest tests/ -v -m "not e2e"
```

**Only unit tests:**
```bash
poetry run pytest tests/unit/ -v
```

**Specific test file:**
```bash
poetry run pytest tests/unit/test_voice_registry.py -v
```

**By marker:**
```bash
poetry run pytest -m unit -v           # Unit tests only
poetry run pytest -m integration -v    # Integration tests only
poetry run pytest -m e2e -v            # E2E tests only
poetry run pytest -m requires_piper -v # Tests requiring Piper CLI
```

## Writing Tests

### Unit Test Template

```python
import pytest
from unittest.mock import patch

@pytest.fixture
def component():
    return MyComponent()

def test_something(component):
    """Test a specific behavior."""
    result = component.do_something()
    assert result is not None
```

### Integration Test Template

```python
import pytest

@pytest.mark.integration
def test_two_systems_work_together():
    """Test System A + System B together."""
    system_a = SystemA()
    system_b = SystemB()
    
    result = system_a.call_system_b(system_b)
    assert result.is_valid()
```

### E2E Test Template

```python
import pytest

@pytest.mark.e2e
def test_cli_command():
    """Test actual CLI command end-to-end."""
    try:
        result = subprocess.run(["voxmancer", "workflow", "--demo"])
        assert result.returncode == 0
    except FileNotFoundError:
        pytest.skip("voxmancer CLI not available")
```

## Dependencies

- **Unit tests** - No external dependencies (all mocked)
- **Integration tests** - Requires Piper TTS, LLM (Ollama or Anthropic)
- **E2E tests** - Requires Piper TTS, LLM, FFmpeg, full environment setup

## CI/CD

In CI/CD pipelines:

1. Always run unit tests (fast, no external deps)
2. Run integration tests if Piper/LLM available
3. Skip E2E tests or run only in nightly builds (slow)

```bash
# Fast CI pipeline
pytest tests/unit/ -v

# Full pipeline (requires setup)
pytest tests/ -v -m "not e2e"

# Nightly (everything)
pytest tests/ -v
```
