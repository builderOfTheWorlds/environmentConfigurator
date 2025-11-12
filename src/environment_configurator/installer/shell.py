"""
Shell configuration management.

Handles installation and configuration of Oh-My-Zsh, Oh-My-Posh, and related tools.
"""

from pathlib import Path
from typing import Optional

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.shell_utils import (
    is_command_available,
    run_command,
    detect_shell,
    get_shell_rc_path,
)

logger = get_logger(__name__)


class ShellConfigurator:
    """Manages shell configuration and installation."""

    def __init__(self, install_dir: Path, test_mode: bool = False):
        """
        Initialize the shell configurator.

        Args:
            install_dir: Base installation directory
            test_mode: Whether running in test mode (no actual changes)
        """
        self.install_dir = install_dir
        self.test_mode = test_mode

    def is_oh_my_zsh_installed(self) -> bool:
        """
        Check if Oh-My-Zsh is already installed.

        Returns:
            True if Oh-My-Zsh is installed, False otherwise
        """
        oh_my_zsh_dir = Path.home() / ".oh-my-zsh"
        is_installed = oh_my_zsh_dir.exists()
        logger.debug(f"Oh-My-Zsh installed: {is_installed}")
        return is_installed

    def is_oh_my_posh_installed(self) -> bool:
        """
        Check if Oh-My-Posh is already installed.

        Returns:
            True if Oh-My-Posh is installed, False otherwise
        """
        is_installed = is_command_available("oh-my-posh")
        logger.debug(f"Oh-My-Posh installed: {is_installed}")
        return is_installed

    def install_oh_my_zsh(self) -> bool:
        """
        Install Oh-My-Zsh.

        Returns:
            True if installation successful, False otherwise
        """
        if self.is_oh_my_zsh_installed():
            logger.info("Oh-My-Zsh already installed")
            return True

        if self.test_mode:
            logger.info("[TEST MODE] Would install Oh-My-Zsh")
            return True

        # Check if zsh is installed
        if not is_command_available("zsh"):
            logger.warning("Zsh is not installed, cannot install Oh-My-Zsh")
            return False

        # Check for installer script
        installer_script = self.install_dir / "scripts" / "install-ohmyzsh.sh"

        if not installer_script.exists():
            logger.error(f"Oh-My-Zsh installer script not found: {installer_script}")
            return False

        try:
            logger.info("Installing Oh-My-Zsh...")
            run_command(
                ["bash", str(installer_script)],
                check=True,
                capture_output=False,
                timeout=300,
            )
            logger.info("Oh-My-Zsh installed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to install Oh-My-Zsh: {e}")
            return False

    def install_oh_my_posh(self) -> bool:
        """
        Install Oh-My-Posh.

        Returns:
            True if installation successful, False otherwise
        """
        if self.is_oh_my_posh_installed():
            logger.info(f"Oh-My-Posh already installed: {self._get_oh_my_posh_version()}")
            return True

        if self.test_mode:
            logger.info("[TEST MODE] Would install Oh-My-Posh")
            return True

        # Ensure ~/bin exists
        bin_dir = Path.home() / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        try:
            logger.info("Installing Oh-My-Posh...")

            # Download and run installer
            install_cmd = (
                "curl -s https://ohmyposh.dev/install.sh | "
                f"bash -s -- -d {bin_dir}"
            )

            run_command(
                ["bash", "-c", install_cmd],
                check=True,
                capture_output=False,
                timeout=300,
            )

            logger.info("Oh-My-Posh installed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to install Oh-My-Posh: {e}")
            return False

    def _get_oh_my_posh_version(self) -> Optional[str]:
        """Get installed Oh-My-Posh version."""
        try:
            returncode, stdout, _ = run_command(
                ["oh-my-posh", "version"],
                check=False,
                capture_output=True,
                timeout=5,
            )
            if returncode == 0:
                return stdout.strip()
        except Exception:
            pass
        return None

    def set_default_shell(self, shell: str = "zsh") -> bool:
        """
        Set the default shell for the current user.

        Args:
            shell: The shell to set as default (e.g., 'zsh', 'bash')

        Returns:
            True if shell changed successfully, False otherwise
        """
        if self.test_mode:
            logger.info(f"[TEST MODE] Would set default shell to: {shell}")
            return True

        if not is_command_available(shell):
            logger.error(f"Shell not available: {shell}")
            return False

        try:
            # Get shell path
            returncode, shell_path, _ = run_command(
                ["which", shell],
                check=False,
                capture_output=True,
            )

            if returncode != 0:
                logger.error(f"Could not locate {shell} binary")
                return False

            shell_path = shell_path.strip()

            # Change default shell
            logger.info(f"Setting default shell to: {shell_path}")
            run_command(
                ["chsh", "-s", shell_path],
                check=True,
                capture_output=False,
            )

            logger.info(f"Default shell changed to {shell}. Please log out and back in.")
            return True

        except Exception as e:
            logger.error(f"Failed to change default shell: {e}")
            return False

    def add_path_to_shell_rc(self, directory: Path) -> bool:
        """
        Add a directory to PATH in the shell RC file.

        Args:
            directory: The directory to add to PATH

        Returns:
            True if added successfully, False otherwise
        """
        shell_rc = get_shell_rc_path()

        if self.test_mode:
            logger.info(f"[TEST MODE] Would add {directory} to PATH in {shell_rc}")
            return True

        try:
            with open(shell_rc, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if already in PATH
            dir_str = str(directory)
            if dir_str in content:
                logger.debug(f"Directory already in PATH: {directory}")
                return True

            # Add to PATH
            shell_name = detect_shell()

            if shell_name in ("bash", "zsh"):
                path_line = f'\n# Add {directory} to PATH\nexport PATH="{directory}:$PATH"\n'
            elif shell_name == "fish":
                path_line = f'\n# Add {directory} to PATH\nset -gx PATH "{directory}" $PATH\n'
            else:
                path_line = f'\n# Add {directory} to PATH\nexport PATH="{directory}:$PATH"\n'

            with open(shell_rc, "a", encoding="utf-8") as f:
                f.write(path_line)

            logger.info(f"Added {directory} to PATH in {shell_rc}")
            return True

        except Exception as e:
            logger.error(f"Failed to add {directory} to PATH: {e}")
            return False
