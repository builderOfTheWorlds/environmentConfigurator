"""
Shell command utilities for environment configurator.

Provides safe command execution, shell detection, and related utilities.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from environment_configurator.utils.logger import get_logger

logger = get_logger(__name__)


def run_command(
    command: List[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    check: bool = True,
    capture_output: bool = True,
    timeout: Optional[int] = None,
) -> Tuple[int, str, str]:
    """
    Run a shell command with proper error handling and logging.

    Args:
        command: The command to run as a list of arguments
        cwd: Working directory for the command
        env: Environment variables for the command
        check: Whether to raise exception on non-zero exit code
        capture_output: Whether to capture stdout/stderr
        timeout: Optional timeout in seconds

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        subprocess.CalledProcessError: If check=True and command fails
        subprocess.TimeoutExpired: If command times out

    Example:
        >>> returncode, stdout, stderr = run_command(["git", "status"])
        >>> print(stdout)
    """
    logger.debug(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
        )

        return_code = result.returncode
        stdout = result.stdout if capture_output else ""
        stderr = result.stderr if capture_output else ""

        if return_code == 0:
            logger.debug(f"Command succeeded: {' '.join(command)}")
        else:
            logger.warning(f"Command failed with code {return_code}: {' '.join(command)}")

        return return_code, stdout, stderr

    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(command)}: {e}")
        raise
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out: {' '.join(command)}")
        raise
    except FileNotFoundError as e:
        logger.error(f"Command not found: {command[0]}")
        raise


def is_command_available(command: str) -> bool:
    """
    Check if a command is available in the system PATH.

    Args:
        command: The command name to check

    Returns:
        True if command is available, False otherwise

    Example:
        >>> if is_command_available("git"):
        ...     print("Git is installed")
    """
    available = shutil.which(command) is not None
    logger.debug(f"Command '{command}' available: {available}")
    return available


def detect_shell() -> str:
    """
    Detect the current user's shell.

    Returns:
        The shell name ('bash', 'zsh', etc.)

    Example:
        >>> shell = detect_shell()
        >>> print(f"Current shell: {shell}")
    """
    shell_path = os.environ.get("SHELL", "/bin/bash")
    shell_name = Path(shell_path).name
    logger.debug(f"Detected shell: {shell_name}")
    return shell_name


def get_shell_rc_path() -> Path:
    """
    Get the path to the current shell's RC file.

    Returns:
        Path to the shell RC file (.bashrc, .zshrc, etc.)

    Example:
        >>> rc_path = get_shell_rc_path()
        >>> print(f"Shell RC: {rc_path}")
    """
    shell = detect_shell()
    home = Path.home()

    shell_rc_map = {
        "bash": home / ".bashrc",
        "zsh": home / ".zshrc",
        "fish": home / ".config" / "fish" / "config.fish",
        "sh": home / ".profile",
    }

    rc_path = shell_rc_map.get(shell, home / ".bashrc")
    logger.debug(f"Shell RC path: {rc_path}")
    return rc_path


def add_to_path(directory: Path, shell_rc: Optional[Path] = None) -> None:
    """
    Add a directory to the PATH in the shell RC file.

    Args:
        directory: The directory to add to PATH
        shell_rc: Optional shell RC file (auto-detected if not provided)

    Example:
        >>> add_to_path(Path.home() / "bin")
    """
    if shell_rc is None:
        shell_rc = get_shell_rc_path()

    # Check if already in PATH
    with open(shell_rc, "r", encoding="utf-8") as f:
        content = f.read()

    path_str = str(directory)
    if path_str in content:
        logger.debug(f"Directory already in PATH: {directory}")
        return

    # Add to PATH
    shell = detect_shell()

    if shell in ("bash", "zsh"):
        path_line = f'\nexport PATH="{directory}:$PATH"\n'
    elif shell == "fish":
        path_line = f'\nset -gx PATH "{directory}" $PATH\n'
    else:
        path_line = f'\nexport PATH="{directory}:$PATH"\n'

    with open(shell_rc, "a", encoding="utf-8") as f:
        f.write(path_line)

    logger.info(f"Added {directory} to PATH in {shell_rc}")


def check_git_installed() -> bool:
    """
    Check if git is installed.

    Returns:
        True if git is installed, False otherwise
    """
    return is_command_available("git")


def check_python_version() -> Tuple[int, int, int]:
    """
    Check the Python version.

    Returns:
        Tuple of (major, minor, micro) version numbers

    Example:
        >>> major, minor, micro = check_python_version()
        >>> print(f"Python {major}.{minor}.{micro}")
    """
    import sys

    version = sys.version_info
    logger.debug(f"Python version: {version.major}.{version.minor}.{version.micro}")
    return version.major, version.minor, version.micro


def get_terminal_size() -> Tuple[int, int]:
    """
    Get the current terminal size.

    Returns:
        Tuple of (width, height) in characters

    Example:
        >>> width, height = get_terminal_size()
        >>> print(f"Terminal: {width}x{height}")
    """
    size = shutil.get_terminal_size()
    return size.columns, size.lines
