"""Installer modules for environment configurator."""

from environment_configurator.installer.auth import GitAuthenticator
from environment_configurator.installer.backup import BackupManager
from environment_configurator.installer.dotfiles import DotfileManager
from environment_configurator.installer.fonts import FontInstaller
from environment_configurator.installer.shell import ShellConfigurator
from environment_configurator.installer.cron import CronManager
from environment_configurator.installer.installer import EnvironmentInstaller

__all__ = [
    "GitAuthenticator",
    "BackupManager",
    "DotfileManager",
    "FontInstaller",
    "ShellConfigurator",
    "CronManager",
    "EnvironmentInstaller",
]
