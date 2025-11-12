"""
CLI wrapper for tmux session manager.

Wraps the existing tmux-session-manager.py script.
"""

import sys
from pathlib import Path

import click

from environment_configurator import __version__


@click.command()
@click.version_option(version=__version__)
@click.argument("args", nargs=-1)
def main(args: tuple) -> None:
    """
    Tmux Session Manager - Manage tmux-resurrect backup files.

    This is a wrapper for the existing tmux-session-manager.py script.
    Run without arguments to see available commands.
    """
    # Find the original script
    original_script = (
        Path(__file__).parent.parent.parent.parent / "scripts" / "tmux-session-manager.py"
    )

    if not original_script.exists():
        click.secho("Error: tmux-session-manager.py not found", fg="red")
        sys.exit(1)

    # Execute the original script with arguments
    import subprocess

    result = subprocess.run([sys.executable, str(original_script), *args])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
