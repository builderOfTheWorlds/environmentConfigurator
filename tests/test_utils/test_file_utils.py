"""Tests for file utility functions."""

from pathlib import Path
import pytest

from environment_configurator.utils.file_utils import (
    ensure_directory,
    backup_file,
    safe_write_file,
    create_symlink,
    read_file,
    get_file_size,
    is_safe_to_overwrite,
)


def test_ensure_directory(temp_dir: Path) -> None:
    """Test directory creation."""
    test_dir = temp_dir / "test" / "nested" / "dir"
    ensure_directory(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()


def test_backup_file(temp_file: Path, temp_dir: Path) -> None:
    """Test file backup."""
    backup_path = backup_file(temp_file, backup_dir=temp_dir, timestamp=False)

    assert backup_path is not None
    assert backup_path.exists()
    assert backup_path.read_text() == temp_file.read_text()


def test_backup_nonexistent_file(temp_dir: Path) -> None:
    """Test backup of nonexistent file."""
    nonexistent = temp_dir / "nonexistent.txt"
    backup_path = backup_file(nonexistent)

    assert backup_path is None


def test_safe_write_file(temp_dir: Path) -> None:
    """Test safe file writing."""
    file_path = temp_dir / "test.txt"
    content = "test content"

    safe_write_file(file_path, content, backup=False)

    assert file_path.exists()
    assert file_path.read_text() == content


def test_safe_write_file_with_backup(temp_file: Path) -> None:
    """Test safe file writing with backup."""
    original_content = temp_file.read_text()
    new_content = "new content"

    safe_write_file(temp_file, new_content, backup=True)

    assert temp_file.read_text() == new_content
    # Backup should exist (with timestamp suffix)
    backups = list(temp_file.parent.glob(f"{temp_file.name}.backup.*"))
    assert len(backups) >= 1


def test_create_symlink(temp_file: Path, temp_dir: Path) -> None:
    """Test symlink creation."""
    link_path = temp_dir / "link.txt"
    create_symlink(temp_file, link_path, force=False, backup=False)

    assert link_path.is_symlink()
    assert link_path.resolve() == temp_file


def test_create_symlink_force(temp_file: Path, temp_dir: Path) -> None:
    """Test symlink creation with force option."""
    link_path = temp_dir / "link.txt"
    link_path.write_text("existing content")

    create_symlink(temp_file, link_path, force=True, backup=False)

    assert link_path.is_symlink()
    assert link_path.resolve() == temp_file


def test_read_file(temp_file: Path) -> None:
    """Test file reading."""
    content = read_file(temp_file)
    assert content == "test content\n"


def test_read_nonexistent_file(temp_dir: Path) -> None:
    """Test reading nonexistent file."""
    with pytest.raises(FileNotFoundError):
        read_file(temp_dir / "nonexistent.txt")


def test_get_file_size(temp_file: Path) -> None:
    """Test getting file size."""
    size = get_file_size(temp_file)
    assert size > 0


def test_is_safe_to_overwrite(temp_file: Path) -> None:
    """Test safe overwrite check."""
    assert is_safe_to_overwrite(temp_file, max_size_mb=1.0)


def test_is_safe_to_overwrite_large_file(temp_dir: Path) -> None:
    """Test safe overwrite check for large file."""
    large_file = temp_dir / "large.txt"
    large_file.write_text("x" * (2 * 1024 * 1024))  # 2MB

    assert not is_safe_to_overwrite(large_file, max_size_mb=1.0)
    assert is_safe_to_overwrite(large_file, max_size_mb=5.0)
