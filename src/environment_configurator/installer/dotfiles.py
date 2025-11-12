"""
Dotfile management for environment configurator.

Handles installation and management of dotfiles via symlinks.
"""

from pathlib import Path
from typing import List

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.file_utils import create_symlink, backup_file

logger = get_logger(__name__)


class DotfileManager:
    """Manages installation of dotfiles."""

    def __init__(self, source_dir: Path, test_mode: bool = False):
        """
        Initialize the dotfile manager.

        Args:
            source_dir: Directory containing the dotfiles
            test_mode: Whether running in test mode (no actual changes)
        """
        self.source_dir = source_dir / "dotfiles"
        self.test_mode = test_mode
        self.installed_files: List[Path] = []

    def get_dotfiles(self) -> List[Path]:
        """
        Get list of all dotfiles in the source directory.

        Returns:
            List of dotfile paths
        """
        if not self.source_dir.exists():
            logger.warning(f"Dotfiles directory not found: {self.source_dir}")
            return []

        dotfiles = []

        # Hidden files (start with .)
        for file_path in self.source_dir.glob(".*"):
            if file_path.is_file() and file_path.name not in (".", ".."):
                dotfiles.append(file_path)

        # Regular files (will be installed with . prefix)
        for file_path in self.source_dir.glob("*"):
            if file_path.is_file():
                dotfiles.append(file_path)

        logger.debug(f"Found {len(dotfiles)} dotfiles")
        return dotfiles

    def install_dotfile(self, source_file: Path, backup: bool = True) -> bool:
        """
        Install a single dotfile via symlink.

        Args:
            source_file: The source dotfile to install
            backup: Whether to backup existing file

        Returns:
            True if installed successfully, False otherwise
        """
        home = Path.home()

        # Determine target filename
        filename = source_file.name
        if not filename.startswith(".") and source_file.parent.name == "dotfiles":
            # Regular filename in dotfiles dir -> add dot prefix
            target_path = home / f".{filename}"
        else:
            target_path = home / filename

        # Test mode - just log what would happen
        if self.test_mode:
            logger.info(f"[TEST MODE] Would link: {target_path} -> {source_file}")
            return True

        # Backup existing file
        if backup and target_path.exists():
            try:
                backup_file(target_path)
            except Exception as e:
                logger.error(f"Failed to backup {target_path}: {e}")
                return False

        # Create symlink
        try:
            create_symlink(source_file, target_path, force=True, backup=False)
            self.installed_files.append(target_path)
            logger.info(f"Installed: {target_path} -> {source_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to install {source_file}: {e}")
            return False

    def install_all(self, backup: bool = True) -> int:
        """
        Install all dotfiles.

        Args:
            backup: Whether to backup existing files

        Returns:
            Number of successfully installed dotfiles
        """
        dotfiles = self.get_dotfiles()

        if not dotfiles:
            logger.warning("No dotfiles found to install")
            return 0

        success_count = 0

        for dotfile in dotfiles:
            if self.install_dotfile(dotfile, backup=backup):
                success_count += 1

        logger.info(f"Installed {success_count}/{len(dotfiles)} dotfiles")
        return success_count

    def uninstall_dotfile(self, target_path: Path) -> bool:
        """
        Uninstall a dotfile symlink.

        Args:
            target_path: The symlink to remove

        Returns:
            True if uninstalled successfully, False otherwise
        """
        if not target_path.exists():
            logger.debug(f"Dotfile not found: {target_path}")
            return False

        if not target_path.is_symlink():
            logger.warning(f"Not a symlink, won't remove: {target_path}")
            return False

        try:
            if self.test_mode:
                logger.info(f"[TEST MODE] Would remove: {target_path}")
            else:
                target_path.unlink()
                logger.info(f"Removed: {target_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove {target_path}: {e}")
            return False

    def get_installed_dotfiles(self) -> List[Path]:
        """
        Get list of currently installed dotfiles.

        Returns:
            List of installed dotfile paths (symlinks)
        """
        return self.installed_files.copy()
