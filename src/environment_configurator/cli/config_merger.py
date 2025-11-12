"""
CLI wrapper for shell config merger.

Wraps the existing merge-bashrc-to-zshrc.py script.
"""

import sys
from pathlib import Path

import click

from environment_configurator import __version__


@click.command()
@click.version_option(version=__version__)
@click.option("--dry-run", is_flag=True, help="Show what would be merged without making changes")
@click.option("--bashrc", type=click.Path(exists=True), help="Path to .bashrc file")
@click.option("--zshrc", type=click.Path(exists=True), help="Path to .zshrc file")
def main(dry_run: bool, bashrc: str, zshrc: str) -> None:
    """
    Merge Bash configuration into Zsh configuration.

    This utility merges .bashrc entries into .zshrc, avoiding duplicates
    and transforming Bash-specific syntax to Zsh equivalents.
    """
    # Find the original script
    original_script = (
        Path(__file__).parent.parent.parent.parent
        / "scripts"
        / "merge-bashrc-to-zshrc.py"
    )

    if not original_script.exists():
        click.secho("Error: merge-bashrc-to-zshrc.py not found", fg="red")
        sys.exit(1)

    # Build arguments
    args = []
    if dry_run:
        args.append("--dry-run")
    if bashrc:
        args.extend(["--bashrc", bashrc])
    if zshrc:
        args.extend(["--zshrc", zshrc])

    # Execute the original script with arguments
    import subprocess

    result = subprocess.run([sys.executable, str(original_script), *args])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
