"""
Pytest configuration and fixtures.

Provides common fixtures for testing.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """Create a temporary file for testing."""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text("test content\n")
    return file_path


@pytest.fixture
def mock_home(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Mock the home directory."""
    home = temp_dir / "home"
    home.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))

    # Patch Path.home() to return our mock home
    monkeypatch.setattr(Path, "home", lambda: home)

    return home


@pytest.fixture
def sample_bashrc(mock_home: Path) -> Path:
    """Create a sample .bashrc file."""
    bashrc = mock_home / ".bashrc"
    bashrc.write_text(
        """
# Sample .bashrc
export PATH=$HOME/bin:$PATH
alias ll='ls -la'
"""
    )
    return bashrc


@pytest.fixture
def sample_zshrc(mock_home: Path) -> Path:
    """Create a sample .zshrc file."""
    zshrc = mock_home / ".zshrc"
    zshrc.write_text(
        """
# Sample .zshrc
export PATH=$HOME/bin:$PATH
"""
    )
    return zshrc
