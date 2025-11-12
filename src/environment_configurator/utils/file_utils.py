"""
File operation utilities for environment configurator.

Provides safe file operations with backups, atomic writes, and error handling.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from environment_configurator.utils.logger import get_logger

logger = get_logger(__name__)


def ensure_directory(path: Path, mode: int = 0o755) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: The directory path to create
        mode: The permissions mode for the directory (default: 0o755)

    Raises:
        OSError: If directory creation fails
    """
    try:
        path.mkdir(parents=True, exist_ok=True, mode=mode)
        logger.debug(f"Ensured directory exists: {path}")
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise


def backup_file(
    file_path: Path,
    backup_dir: Optional[Path] = None,
    timestamp: bool = True,
) -> Optional[Path]:
    """
    Create a backup of a file before modification.

    Args:
        file_path: The file to backup
        backup_dir: Optional directory for backups (default: same as file)
        timestamp: Whether to add timestamp to backup name

    Returns:
        Path to the backup file, or None if original file doesn't exist

    Example:
        >>> backup_path = backup_file(Path.home() / ".bashrc")
        >>> print(f"Backed up to: {backup_path}")
    """
    if not file_path.exists():
        logger.debug(f"No backup needed, file doesn't exist: {file_path}")
        return None

    # Determine backup location
    if backup_dir is None:
        backup_dir = file_path.parent

    ensure_directory(backup_dir)

    # Create backup filename
    if timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup.{ts}"
    else:
        backup_name = f"{file_path.name}.backup"

    backup_path = backup_dir / backup_name

    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up {file_path} to {backup_path}")
        return backup_path
    except (IOError, OSError) as e:
        logger.error(f"Failed to backup {file_path}: {e}")
        raise


def safe_write_file(file_path: Path, content: str, backup: bool = True) -> None:
    """
    Safely write content to a file with optional backup.

    Uses atomic write pattern (write to temp file, then rename).

    Args:
        file_path: The file to write
        content: The content to write
        backup: Whether to backup the existing file first

    Raises:
        IOError: If write operation fails
    """
    # Backup existing file if requested
    if backup and file_path.exists():
        backup_file(file_path)

    # Ensure parent directory exists
    ensure_directory(file_path.parent)

    # Write to temporary file first (atomic write pattern)
    temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Atomic rename
        temp_path.replace(file_path)
        logger.info(f"Wrote file: {file_path}")

    except (IOError, OSError) as e:
        logger.error(f"Failed to write {file_path}: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise


def create_symlink(
    target: Path,
    link_path: Path,
    force: bool = False,
    backup: bool = True,
) -> None:
    """
    Create a symbolic link to a target file or directory.

    Args:
        target: The target file/directory
        link_path: The symlink path to create
        force: Whether to overwrite existing symlink
        backup: Whether to backup existing file before replacing

    Raises:
        FileExistsError: If link exists and force=False
        OSError: If symlink creation fails
    """
    # Check if link already exists
    if link_path.exists() or link_path.is_symlink():
        if not force:
            raise FileExistsError(f"Link already exists: {link_path}")

        # Backup existing file if it's not a symlink
        if backup and not link_path.is_symlink():
            backup_file(link_path)

        # Remove existing link/file
        if link_path.is_symlink():
            link_path.unlink()
        elif link_path.is_file():
            link_path.unlink()
        elif link_path.is_dir():
            shutil.rmtree(link_path)

    # Ensure parent directory exists
    ensure_directory(link_path.parent)

    try:
        link_path.symlink_to(target)
        logger.info(f"Created symlink: {link_path} -> {target}")
    except OSError as e:
        logger.error(f"Failed to create symlink {link_path} -> {target}: {e}")
        raise


def read_file(file_path: Path) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: The file to read

    Returns:
        The file contents as a string

    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If read operation fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.debug(f"Read file: {file_path}")
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Failed to read {file_path}: {e}")
        raise


def get_file_size(file_path: Path) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: The file to check

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path.stat().st_size


def is_safe_to_overwrite(file_path: Path, max_size_mb: float = 100) -> bool:
    """
    Check if it's safe to overwrite a file based on size limits.

    Args:
        file_path: The file to check
        max_size_mb: Maximum file size in MB to consider safe

    Returns:
        True if safe to overwrite, False otherwise
    """
    if not file_path.exists():
        return True

    size_mb = get_file_size(file_path) / (1024 * 1024)
    return size_mb <= max_size_mb
