"""Pytest configuration and shared fixtures."""
import pytest
from pathlib import Path


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def examples_dir(project_root):
    """Get the examples directory."""
    return project_root / "examples"


@pytest.fixture
def cache_dir(tmp_path):
    """Provide a temporary cache directory."""
    cache = tmp_path / "cache"
    cache.mkdir()
    return cache
