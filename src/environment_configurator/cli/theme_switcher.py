"""
CLI for tmux theme switcher.

Provides command-line interface for browsing and applying tmux themes.
"""

import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from environment_configurator import __version__
from environment_configurator.utils.logger import setup_logging, get_logger
from environment_configurator.tmux.theme_manager import ThemeManager
from environment_configurator.tmux.theme_applier import ThemeApplier

logger = get_logger(__name__)
console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Tmux Theme Switcher - Manage your tmux color themes."""
    ctx.ensure_object(dict)

    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_level=log_level, verbose=verbose, enable_file_logging=False)

    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--search", "-s", help="Search themes by name or description")
@click.pass_context
def list(ctx: click.Context, category: str, search: str) -> None:
    """List available themes."""
    manager = ThemeManager()

    # Get themes based on filters
    if search:
        themes = manager.search_themes(search)
        title = f"Search Results for '{search}'"
    elif category:
        themes = manager.get_themes_by_category(category)
        title = f"Themes in Category '{category}'"
    else:
        themes = manager.get_all_themes()
        title = "All Available Themes"

    if not themes:
        console.print("[yellow]No themes found.[/yellow]")
        return

    # Create table
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Category", style="green")
    table.add_column("Description")

    for theme in themes:
        table.add_row(theme.name, theme.category, theme.description)

    console.print(table)
    console.print(f"\n[dim]Total: {len(themes)} themes[/dim]")


@cli.command()
@click.pass_context
def categories(ctx: click.Context) -> None:
    """List theme categories."""
    manager = ThemeManager()
    categories_list = manager.get_categories()

    table = Table(title="Theme Categories", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")

    for cat in categories_list:
        table.add_row(cat.id, cat.display_name, cat.description)

    console.print(table)


@cli.command()
@click.argument("theme_name")
@click.pass_context
def preview(ctx: click.Context, theme_name: str) -> None:
    """Preview a theme's colors."""
    manager = ThemeManager()
    theme = manager.get_theme_by_name(theme_name)

    if not theme:
        console.print(f"[red]Theme not found: {theme_name}[/red]")
        sys.exit(1)

    # Create preview panel
    preview_text = f"""
[bold]{theme.name}[/bold]
Category: {theme.category}
Description: {theme.description}

[bold]Color Palette:[/bold]
  Background:    {theme.bg_color}
  Foreground:    {theme.fg_color}
  Accent:        {theme.accent_color}
  Border:        {theme.border_color}
  Border Active: {theme.border_active}
  Message BG:    {theme.message_bg}
  Message FG:    {theme.message_fg}
  Activity:      {theme.activity_color}

[bold]Shell Configuration:[/bold]
  Dir Color:     {theme.dir_color}
  Bat Theme:     {theme.bat_theme}
"""

    panel = Panel(preview_text, title=f"Theme Preview: {theme.name}", border_style="cyan")
    console.print(panel)


@cli.command()
@click.argument("theme_name")
@click.option("--no-backup", is_flag=True, help="Don't create backups")
@click.option("--force", "-f", is_flag=True, help="Apply without confirmation")
@click.pass_context
def apply(ctx: click.Context, theme_name: str, no_backup: bool, force: bool) -> None:
    """Apply a theme to tmux and shell."""
    manager = ThemeManager()
    theme = manager.get_theme_by_name(theme_name)

    if not theme:
        console.print(f"[red]Theme not found: {theme_name}[/red]")
        console.print("\n[dim]Use 'tmux-theme-switcher list' to see available themes[/dim]")
        sys.exit(1)

    # Show preview
    console.print(f"\n[bold cyan]Theme:[/bold cyan] {theme.name}")
    console.print(f"[dim]{theme.description}[/dim]")

    # Confirm
    if not force:
        console.print("\n[yellow]This will modify:[/yellow]")
        console.print("  • ~/.tmux.conf")
        console.print("  • ~/.bashrc or ~/.zshrc")

        if not no_backup:
            console.print("\n[green]Backups will be created automatically.[/green]")

        if not click.confirm("\nApply this theme?"):
            console.print("[yellow]Cancelled.[/yellow]")
            sys.exit(0)

    # Apply theme
    applier = ThemeApplier(backup_enabled=not no_backup)

    try:
        success = applier.apply_theme(theme)

        if success:
            console.print(f"\n[bold green]✓ Theme '{theme.name}' applied successfully![/bold green]")
            console.print("\n[dim]Restart your shell or source your RC file to see changes:[/dim]")
            console.print("[dim]  source ~/.bashrc  # or ~/.zshrc[/dim]")
            sys.exit(0)
        else:
            console.print(f"\n[bold red]✗ Failed to apply theme '{theme.name}'[/bold red]")
            sys.exit(1)

    except Exception as e:
        logger.exception("Error applying theme")
        console.print(f"\n[bold red]✗ Error: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def current(ctx: click.Context) -> None:
    """Show the currently applied theme."""
    applier = ThemeApplier()
    theme_name = applier.get_current_theme_name()

    if theme_name:
        console.print(f"\n[bold green]Current theme:[/bold green] {theme_name}")

        # Try to get theme details
        manager = ThemeManager()
        theme = manager.get_theme_by_name(theme_name)

        if theme:
            console.print(f"[dim]{theme.description}[/dim]")
    else:
        console.print("\n[yellow]No theme is currently applied.[/yellow]")


@cli.command()
@click.pass_context
def interactive(ctx: click.Context) -> None:
    """Launch the interactive TUI (original theme switcher)."""
    try:
        import curses
        from pathlib import Path
        import sys

        # Try to import the original theme switcher if it exists
        original_script = Path(__file__).parent.parent.parent.parent / "scripts" / "tmux-theme-switcher.py"

        if original_script.exists():
            console.print("[cyan]Launching interactive theme switcher...[/cyan]")
            # Execute the original script
            import subprocess
            subprocess.run([sys.executable, str(original_script)])
        else:
            console.print("[yellow]Interactive TUI not available in this version.[/yellow]")
            console.print("[dim]Use the 'list', 'preview', and 'apply' commands instead.[/dim]")

    except ImportError:
        console.print("[red]Curses library not available on this system.[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show theme statistics."""
    manager = ThemeManager()

    console.print("\n[bold cyan]Theme Statistics[/bold cyan]")
    console.print(f"Total themes: {manager.get_theme_count()}")
    console.print(f"Categories: {manager.get_category_count()}")

    console.print("\n[bold]Themes by category:[/bold]")
    grouped = manager.get_grouped_themes()

    for category, themes in sorted(grouped.items()):
        console.print(f"  {category:12} : {len(themes)} themes")

    console.print()


def main() -> None:
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
