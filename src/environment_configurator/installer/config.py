"""
Configuration management for the installer.

Centralized configuration for repository URLs, paths, and settings.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class InstallerConfig:
    """Configuration for the environment installer."""

    # Repository settings
    repo_url: str = "https://github.com/builderOfTheWorlds/environmentConfigurator.git"
    repo_branch: str = "main"

    # Installation paths
    install_dir: Path = Path.home() / ".environment-config"
    bin_dir: Path = Path.home() / "bin"
    backup_dir: Optional[Path] = None  # Will be set dynamically

    # Dotfiles to install
    dotfiles: list[str] = None  # type: ignore

    # Scripts to install
    scripts_enabled: bool = True

    # Font installation
    fonts_enabled: bool = True
    fonts_dir: Path = Path.home() / ".local" / "share" / "fonts" / "NerdFonts"

    # Auto-update settings
    auto_update_enabled: bool = True
    auto_update_interval: str = "0 */6 * * *"  # Every 6 hours

    # Shell configuration
    oh_my_zsh_enabled: bool = False  # Ask during installation
    oh_my_posh_enabled: bool = False  # Ask during installation

    # Operational settings
    test_mode: bool = False
    verbose: bool = False

    def __post_init__(self) -> None:
        """Initialize default values after dataclass creation."""
        if self.dotfiles is None:
            self.dotfiles = [
                ".bashrc",
                ".zshrc",
                ".gitconfig",
                ".tmux.conf",
            ]

        if self.backup_dir is None:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.backup_dir = Path.home() / f".environment-config-backup-{timestamp}"

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "repo_url": self.repo_url,
            "repo_branch": self.repo_branch,
            "install_dir": str(self.install_dir),
            "bin_dir": str(self.bin_dir),
            "backup_dir": str(self.backup_dir),
            "dotfiles": self.dotfiles,
            "scripts_enabled": self.scripts_enabled,
            "fonts_enabled": self.fonts_enabled,
            "auto_update_enabled": self.auto_update_enabled,
            "test_mode": self.test_mode,
            "verbose": self.verbose,
        }
