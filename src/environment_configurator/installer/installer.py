"""
Main installer orchestrator.

Coordinates all installation components to set up the environment.
"""

import shutil
from pathlib import Path
from typing import Optional

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.shell_utils import check_git_installed, run_command
from environment_configurator.installer.config import InstallerConfig
from environment_configurator.installer.auth import GitAuthenticator
from environment_configurator.installer.backup import BackupManager
from environment_configurator.installer.dotfiles import DotfileManager
from environment_configurator.installer.fonts import FontInstaller
from environment_configurator.installer.shell import ShellConfigurator
from environment_configurator.installer.cron import CronManager

logger = get_logger(__name__)


class EnvironmentInstaller:
    """Main installer class that orchestrates the installation process."""

    def __init__(self, config: InstallerConfig):
        """
        Initialize the environment installer.

        Args:
            config: Installation configuration
        """
        self.config = config

        # Initialize component managers
        self.backup_manager = BackupManager(config.backup_dir)
        self.authenticator: Optional[GitAuthenticator] = None
        self.dotfile_manager: Optional[DotfileManager] = None
        self.font_installer: Optional[FontInstaller] = None
        self.shell_configurator: Optional[ShellConfigurator] = None
        self.cron_manager = CronManager(test_mode=config.test_mode)

    def check_prerequisites(self) -> bool:
        """
        Check if all prerequisites are met.

        Returns:
            True if prerequisites are met, False otherwise
        """
        logger.info("Checking prerequisites...")

        if not check_git_installed():
            logger.error("Git is not installed. Please install git first.")
            return False

        logger.info("Prerequisites check passed")
        return True

    def clone_or_update_repository(self) -> bool:
        """
        Clone or update the configuration repository.

        Returns:
            True if successful, False otherwise
        """
        if self.config.test_mode:
            logger.info("[TEST MODE] Would clone/update repository")
            return True

        # Initialize authenticator
        self.authenticator = GitAuthenticator(self.config.repo_url)

        # Get authenticated URL
        try:
            auth_url = self.authenticator.get_authenticated_url()
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

        # Clone or pull
        if self.config.install_dir.exists():
            logger.info(f"Updating existing installation at {self.config.install_dir}")
            try:
                run_command(
                    ["git", "pull", "origin", self.config.repo_branch],
                    cwd=self.config.install_dir,
                    check=True,
                )
                logger.info("Repository updated successfully")
            except Exception as e:
                logger.error(f"Failed to update repository: {e}")
                return False
        else:
            logger.info(f"Cloning repository to {self.config.install_dir}")
            try:
                run_command(
                    ["git", "clone", auth_url, str(self.config.install_dir)],
                    check=True,
                )
                logger.info("Repository cloned successfully")

                # Configure credential helper
                if self.authenticator:
                    self.authenticator.configure_credential_helper(self.config.install_dir)

            except Exception as e:
                logger.error(f"Failed to clone repository: {e}")
                return False

        return True

    def backup_existing_files(self) -> bool:
        """
        Backup existing configuration files.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Backing up existing configuration files...")

        if self.config.test_mode:
            logger.info("[TEST MODE] Would backup existing files")
            return True

        try:
            backed_up = self.backup_manager.backup_dotfiles()
            logger.info(f"Backed up {len(backed_up)} files")
            return True
        except Exception as e:
            logger.error(f"Failed to backup files: {e}")
            return False

    def install_dotfiles(self) -> bool:
        """
        Install dotfiles via symlinks.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Installing dotfiles...")

        self.dotfile_manager = DotfileManager(
            self.config.install_dir,
            test_mode=self.config.test_mode,
        )

        try:
            count = self.dotfile_manager.install_all(backup=True)
            logger.info(f"Installed {count} dotfiles")
            return count > 0
        except Exception as e:
            logger.error(f"Failed to install dotfiles: {e}")
            return False

    def install_scripts(self) -> bool:
        """
        Install scripts to ~/bin.

        Returns:
            True if successful, False otherwise
        """
        if not self.config.scripts_enabled:
            logger.info("Script installation disabled")
            return True

        logger.info("Installing scripts...")

        if self.config.test_mode:
            logger.info("[TEST MODE] Would install scripts")
            return True

        scripts_dir = self.config.install_dir / "scripts"

        if not scripts_dir.exists():
            logger.warning(f"Scripts directory not found: {scripts_dir}")
            return False

        # Ensure bin directory exists
        self.config.bin_dir.mkdir(parents=True, exist_ok=True)

        try:
            installed_count = 0

            for script in scripts_dir.glob("*"):
                if script.is_file() and not script.name.startswith("."):
                    target = self.config.bin_dir / script.name

                    # Create symlink
                    if target.exists() or target.is_symlink():
                        target.unlink()

                    target.symlink_to(script)

                    # Make executable
                    target.chmod(0o755)

                    installed_count += 1
                    logger.debug(f"Installed script: {script.name}")

            logger.info(f"Installed {installed_count} scripts to {self.config.bin_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to install scripts: {e}")
            return False

    def add_bin_to_path(self) -> bool:
        """
        Add ~/bin to PATH in shell RC file.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Adding ~/bin to PATH...")

        self.shell_configurator = ShellConfigurator(
            self.config.install_dir,
            test_mode=self.config.test_mode,
        )

        try:
            return self.shell_configurator.add_path_to_shell_rc(self.config.bin_dir)
        except Exception as e:
            logger.error(f"Failed to add ~/bin to PATH: {e}")
            return False

    def install_fonts(self) -> bool:
        """
        Install Nerd Fonts.

        Returns:
            True if successful, False otherwise
        """
        if not self.config.fonts_enabled:
            logger.info("Font installation disabled")
            return True

        logger.info("Installing fonts...")

        self.font_installer = FontInstaller(
            self.config.install_dir,
            fonts_dir=self.config.fonts_dir,
            test_mode=self.config.test_mode,
        )

        try:
            return self.font_installer.install_all()
        except Exception as e:
            logger.error(f"Failed to install fonts: {e}")
            return False

    def setup_auto_update(self) -> bool:
        """
        Set up automatic updates via cron.

        Returns:
            True if successful, False otherwise
        """
        if not self.config.auto_update_enabled:
            logger.info("Auto-update disabled")
            return True

        logger.info("Setting up auto-update...")

        try:
            return self.cron_manager.add_auto_update_job(
                self.config.install_dir,
                schedule=self.config.auto_update_interval,
                branch=self.config.repo_branch,
            )
        except Exception as e:
            logger.error(f"Failed to setup auto-update: {e}")
            return False

    def create_update_command(self) -> bool:
        """
        Create update-env-config command in ~/bin.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Creating update command...")

        if self.config.test_mode:
            logger.info("[TEST MODE] Would create update command")
            return True

        update_script = self.config.bin_dir / "update-env-config"

        script_content = f"""#!/bin/bash
# Environment Configurator - Manual Update Script
cd "{self.config.install_dir}" && git pull origin {self.config.repo_branch}
echo "Environment configuration updated!"
"""

        try:
            update_script.write_text(script_content)
            update_script.chmod(0o755)
            logger.info(f"Created update command: {update_script}")
            return True

        except Exception as e:
            logger.error(f"Failed to create update command: {e}")
            return False

    def install(self) -> bool:
        """
        Run the complete installation process.

        Returns:
            True if installation successful, False otherwise
        """
        logger.info("Starting environment configuration installation...")

        if self.config.test_mode:
            logger.info("=" * 60)
            logger.info("RUNNING IN TEST MODE - NO CHANGES WILL BE MADE")
            logger.info("=" * 60)

        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            logger.error("Prerequisites check failed")
            return False

        # Step 2: Backup existing files
        if not self.backup_existing_files():
            logger.warning("Backup failed, but continuing...")

        # Step 3: Clone or update repository
        if not self.clone_or_update_repository():
            logger.error("Failed to clone/update repository")
            return False

        # Step 4: Install dotfiles
        if not self.install_dotfiles():
            logger.warning("Dotfile installation had issues, but continuing...")

        # Step 5: Install scripts
        if not self.install_scripts():
            logger.warning("Script installation had issues, but continuing...")

        # Step 6: Add bin to PATH
        if not self.add_bin_to_path():
            logger.warning("Failed to add ~/bin to PATH, but continuing...")

        # Step 7: Install fonts
        if not self.install_fonts():
            logger.warning("Font installation had issues, but continuing...")

        # Step 8: Setup auto-update
        if not self.setup_auto_update():
            logger.warning("Auto-update setup failed, but continuing...")

        # Step 9: Create update command
        if not self.create_update_command():
            logger.warning("Failed to create update command, but continuing...")

        logger.info("=" * 60)
        logger.info("Installation completed successfully!")
        logger.info("=" * 60)

        return True

    def uninstall(self) -> bool:
        """
        Uninstall the environment configuration.

        Returns:
            True if uninstallation successful, False otherwise
        """
        logger.info("Starting environment configuration uninstallation...")

        if self.config.test_mode:
            logger.info("[TEST MODE] Would uninstall environment configuration")
            return True

        # Remove cron job
        self.cron_manager.remove_auto_update_job(self.config.install_dir)

        # Remove installation directory
        if self.config.install_dir.exists():
            try:
                shutil.rmtree(self.config.install_dir)
                logger.info(f"Removed installation directory: {self.config.install_dir}")
            except Exception as e:
                logger.error(f"Failed to remove installation directory: {e}")

        logger.info("Uninstallation completed")
        return True
