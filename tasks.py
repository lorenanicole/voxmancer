"""Invoke tasks for Voxmancer development."""
from invoke import task


@task
def lint(c):
    """Run ruff lint check."""
    c.run("ruff check voxmancer tests")


@task
def format(c):
    """Format code with ruff."""
    c.run("ruff format voxmancer tests")


@task
def format_check(c):
    """Check code formatting without modifying."""
    c.run("ruff format --check voxmancer tests")


@task
def test_unit(c):
    """Run unit tests only."""
    c.run("poetry run pytest tests/unit/ -v")


@task
def test_integration(c):
    """Run integration tests."""
    c.run("poetry run pytest tests/integration/ -v")


@task
def test_e2e(c):
    """Run end-to-end tests (slow)."""
    c.run("poetry run pytest tests/e2e/ -v -m e2e")


@task
def test_fast(c):
    """Run fast tests (unit + integration, skip E2E)."""
    c.run("poetry run pytest tests/ -v -m 'not e2e'")


@task
def test_all(c):
    """Run all tests."""
    c.run("poetry run pytest tests/ -v")


@task
def test(c):
    """Run all tests (alias)."""
    test_all(c)


@task
def check(c):
    """Run linting and formatting checks."""
    print("🔍 Running lint check...")
    lint(c)
    print("\n📝 Checking format...")
    format_check(c)


@task
def ci(c):
    """Run CI pipeline (lint + format check + fast tests)."""
    print("🔍 Linting...")
    lint(c)
    print("\n📝 Checking format...")
    format_check(c)
    print("\n🧪 Running tests...")
    test_fast(c)
    print("\n✅ CI pipeline passed!")


@task
def download_voices(c):
    """Pre-download all Piper voices for demo."""
    c.run("python3 scripts/download_voices.py")


@task
def setup_hooks(c):
    """Set up git pre-commit hook."""
    hook_content = """#!/bin/bash
# Pre-commit hook to run ruff lint and format

echo "🔍 Running ruff lint..."
poetry run ruff check voxmancer tests
if [ $? -ne 0 ]; then
    echo "❌ Lint failed. Fix errors or run: inv format"
    exit 1
fi

echo "📝 Checking ruff format..."
poetry run ruff format --check voxmancer tests
if [ $? -ne 0 ]; then
    echo "❌ Format check failed. Run: inv format"
    exit 1
fi

echo "✅ Pre-commit checks passed!"
exit 0
"""

    hook_path = ".git/hooks/pre-commit"
    with open(hook_path, "w") as f:
        f.write(hook_content)

    c.run(f"chmod +x {hook_path}")
    print(f"✅ Pre-commit hook installed at {hook_path}")
    print("Run 'inv format' to auto-fix format issues")
