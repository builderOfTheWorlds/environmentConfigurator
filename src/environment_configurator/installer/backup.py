"""
Backup management for environment configurator.

Handles creating, managing, and restoring backups of configuration files.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.file_utils import ensure_directory

logger = get_logger(__name__)


class BackupManager:
    """Manages backups of configuration files."""

    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize the backup manager.

        Args:
            backup_dir: Directory for backups (auto-generated if not provided)
        """
        if backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_dir = Path.home() / f".environment-config-backup-{timestamp}"

        self.backup_dir = backup_dir
        self.backed_up_files: List[Path] = []

    def create_backup_directory(self) -> None:
        """Create the backup directory if it doesn't exist."""
        ensure_directory(self.backup_dir)
        logger.info(f"Backup directory: {self.backup_dir}")

    def backup_file(self, file_path: Path) -> Optional[Path]:
        """
        Backup a single file.

        Args:
            file_path: The file to backup

        Returns:
            Path to the backup file, or None if file doesn't exist
        """
        if not file_path.exists():
            logger.debug(f"File doesn't exist, skipping backup: {file_path}")
            return None

        self.create_backup_directory()

        backup_path = self.backup_dir / file_path.name

        try:
            shutil.copy2(file_path, backup_path)
            self.backed_up_files.append(backup_path)
            logger.info(f"Backed up: {file_path} -> {backup_path}")
            return backup_path

        except (IOError, OSError) as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            raise

    def backup_files(self, file_paths: List[Path]) -> List[Path]:
        """
        Backup multiple files.

        Args:
            file_paths: List of files to backup

        Returns:
            List of backup file paths (excludes files that didn't exist)
        """
        backed_up = []

        for file_path in file_paths:
            backup_path = self.backup_file(file_path)
            if backup_path:
                backed_up.append(backup_path)

        logger.info(f"Backed up {len(backed_up)} files to {self.backup_dir}")
        return backed_up

    def backup_dotfiles(self) -> List[Path]:
        """
        Backup common dotfiles from home directory.

        Returns:
            List of backed up file paths
        """
        home = Path.home()
        dotfiles = [
            home / ".bashrc",
            home / ".zshrc",
            home / ".gitconfig",
            home / ".tmux.conf",
            home / ".profile",
        ]

        return self.backup_files(dotfiles)

    def restore_file(self, backup_path: Path, restore_to: Optional[Path] = None) -> None:
        """
        Restore a file from backup.

        Args:
            backup_path: The backup file to restore from
            restore_to: Optional destination path (auto-detected if not provided)

        Raises:
            FileNotFoundError: If backup file doesn't exist
            IOError: If restore operation fails
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        if restore_to is None:
            # Auto-detect: remove .backup.TIMESTAMP suffix
            filename = backup_path.name.split(".backup")[0]
            restore_to = Path.home() / filename

        try:
            shutil.copy2(backup_path, restore_to)
            logger.info(f"Restored: {backup_path} -> {restore_to}")

        except (IOError, OSError) as e:
            logger.error(f"Failed to restore {backup_path}: {e}")
            raise

    def list_backups(self) -> List[Path]:
        """
        List all files in the backup directory.

        Returns:
            List of backup file paths
        """
        if not self.backup_dir.exists():
            return []

        backups = sorted(self.backup_dir.glob("*"))
        return [b for b in backups if b.is_file()]

    def get_backup_info(self) -> dict:
        """
        Get information about the backup.

        Returns:
            Dictionary with backup information
        """
        backups = self.list_backups()

        return {
            "backup_dir": str(self.backup_dir),
            "num_files": len(backups),
            "files": [b.name for b in backups],
            "total_size_mb": sum(b.stat().st_size for b in backups) / (1024 * 1024),
            "created": (
                datetime.fromtimestamp(self.backup_dir.stat().st_ctime).isoformat()
                if self.backup_dir.exists()
                else None
            ),
        }

    def cleanup_old_backups(self, keep_last: int = 5) -> int:
        """
        Clean up old backup directories, keeping only the most recent ones.

        Args:
            keep_last: Number of recent backups to keep

        Returns:
            Number of backup directories deleted
        """
        backup_parent = Path.home()
        backup_pattern = ".environment-config-backup-*"

        # Find all backup directories
        backup_dirs = sorted(
            [d for d in backup_parent.glob(backup_pattern) if d.is_dir()],
            key=lambda d: d.stat().st_ctime,
            reverse=True,
        )

        # Keep only the most recent ones
        to_delete = backup_dirs[keep_last:]
        deleted_count = 0

        for backup_dir in to_delete:
            try:
                shutil.rmtree(backup_dir)
                logger.info(f"Deleted old backup: {backup_dir}")
                deleted_count += 1
            except OSError as e:
                logger.warning(f"Could not delete backup {backup_dir}: {e}")

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old backup directories")

        return deleted_count
