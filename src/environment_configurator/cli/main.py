"""
Main CLI for environment configurator.

Provides the primary command-line interface for installation and management.
"""

import logging
import sys
from pathlib import Path

import click

from environment_configurator import __version__
from environment_configurator.utils.logger import setup_logging, get_logger
from environment_configurator.installer.config import InstallerConfig
from environment_configurator.installer.installer import EnvironmentInstaller

logger = get_logger(__name__)


@click.group()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option("--log-file", type=click.Path(), help="Log file path")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, log_file: str) -> None:
    """Environment Configurator - Manage your development environment."""
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    log_path = Path(log_file) if log_file else None

    setup_logging(
        log_level=log_level,
        log_file=log_path,
        verbose=verbose,
        enable_file_logging=True,
    )

    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--test", is_flag=True, help="Run in test mode (no changes)")
@click.option(
    "--repo-url",
    default="https://github.com/builderOfTheWorlds/environmentConfigurator.git",
    help="Repository URL",
)
@click.option("--branch", default="main", help="Repository branch")
@click.option("--install-dir", type=click.Path(), help="Installation directory")
@click.option("--no-fonts", is_flag=True, help="Skip font installation")
@click.option("--no-auto-update", is_flag=True, help="Disable auto-update")
@click.option("--use-password", is_flag=True, help="Use password auth (deprecated)")
@click.pass_context
def install(
    ctx: click.Context,
    test: bool,
    repo_url: str,
    branch: str,
    install_dir: str,
    no_fonts: bool,
    no_auto_update: bool,
    use_password: bool,
) -> None:
    """Install the environment configuration."""
    verbose = ctx.obj.get("verbose", False)

    logger.info(f"Environment Configurator v{__version__}")
    logger.info("Starting installation...")

    # Create configuration
    config = InstallerConfig(
        repo_url=repo_url,
        repo_branch=branch,
        test_mode=test,
        verbose=verbose,
        fonts_enabled=not no_fonts,
        auto_update_enabled=not no_auto_update,
    )

    if install_dir:
        config.install_dir = Path(install_dir)

    # Run installation
    installer = EnvironmentInstaller(config)

    try:
        success = installer.install()

        if success:
            click.secho("\n✓ Installation completed successfully!", fg="green", bold=True)

            if not test:
                click.echo("\nNext steps:")
                click.echo("1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)")
                click.echo("2. Run 'update-env-config' anytime to pull latest changes")
                click.echo("3. Run 'tmux-theme-switcher' to customize your tmux theme")

            sys.exit(0)
        else:
            click.secho("\n✗ Installation failed. Check logs for details.", fg="red", bold=True)
            sys.exit(1)

    except Exception as e:
        logger.exception("Installation error")
        click.secho(f"\n✗ Installation error: {e}", fg="red", bold=True)
        sys.exit(1)


@cli.command()
@click.option("--test", is_flag=True, help="Run in test mode (no changes)")
@click.pass_context
def uninstall(ctx: click.Context, test: bool) -> None:
    """Uninstall the environment configuration."""
    verbose = ctx.obj.get("verbose", False)

    if not test:
        click.confirm(
            "This will remove the environment configuration. Continue?",
            abort=True,
        )

    config = InstallerConfig(test_mode=test, verbose=verbose)
    installer = EnvironmentInstaller(config)

    try:
        success = installer.uninstall()

        if success:
            click.secho("\n✓ Uninstallation completed successfully!", fg="green", bold=True)
            sys.exit(0)
        else:
            click.secho("\n✗ Uninstallation failed.", fg="red", bold=True)
            sys.exit(1)

    except Exception as e:
        logger.exception("Uninstallation error")
        click.secho(f"\n✗ Uninstallation error: {e}", fg="red", bold=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show installation status."""
    config = InstallerConfig()

    click.echo("\n" + "=" * 60)
    click.echo("Environment Configurator Status")
    click.echo("=" * 60)

    # Check if installed
    if config.install_dir.exists():
        click.secho(f"\n✓ Installed at: {config.install_dir}", fg="green")

        # Check for dotfiles
        home = Path.home()
        dotfiles = [".bashrc", ".zshrc", ".gitconfig", ".tmux.conf"]
        linked_dotfiles = []

        for dotfile in dotfiles:
            path = home / dotfile
            if path.is_symlink():
                target = path.resolve()
                if str(config.install_dir) in str(target):
                    linked_dotfiles.append(dotfile)

        if linked_dotfiles:
            click.echo(f"\nLinked dotfiles: {', '.join(linked_dotfiles)}")

        # Check for scripts
        if config.bin_dir.exists():
            scripts = list(config.bin_dir.glob("*"))
            click.echo(f"\nScripts in ~/bin: {len(scripts)}")

    else:
        click.secho(f"\n✗ Not installed (expected at: {config.install_dir})", fg="red")

    click.echo("\n" + "=" * 60)


@cli.command()
def info() -> None:
    """Show system information."""
    from environment_configurator.utils.shell_utils import (
        detect_shell,
        check_python_version,
        get_terminal_size,
    )

    click.echo("\n" + "=" * 60)
    click.echo("System Information")
    click.echo("=" * 60)

    # Python version
    major, minor, micro = check_python_version()
    click.echo(f"\nPython: {major}.{minor}.{micro}")

    # Shell
    shell = detect_shell()
    click.echo(f"Shell: {shell}")

    # Terminal size
    width, height = get_terminal_size()
    click.echo(f"Terminal: {width}x{height}")

    # Home directory
    click.echo(f"Home: {Path.home()}")

    click.echo("\n" + "=" * 60)


def main() -> None:
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
