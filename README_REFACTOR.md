# Environment Configurator v2.0 - Refactored

## Overview

The Environment Configurator has been completely refactored into an enterprise-level Python project with:

- **Modular architecture** - Separated concerns into focused modules
- **Comprehensive logging** - Enterprise-grade logging with rotation and levels
- **Extensive testing** - pytest test suite with good coverage
- **Modern CLI** - Click-based interfaces with rich output
- **Type safety** - Full type hints throughout the codebase
- **YAML configuration** - Themes and settings in readable YAML files
- **Proper packaging** - Installable via pip with entry points

## Project Structure

```
environmentConfigurator/
├── src/
│   └── environment_configurator/
│       ├── __init__.py
│       ├── cli/                    # Command-line interfaces
│       │   ├── main.py            # env-config command
│       │   ├── theme_switcher.py  # tmux-theme-switcher command
│       │   ├── session_manager.py # tmux-session-manager command
│       │   └── config_merger.py   # merge-shell-config command
│       ├── installer/              # Installation modules
│       │   ├── auth.py            # Git authentication
│       │   ├── backup.py          # Backup management
│       │   ├── dotfiles.py        # Dotfile installation
│       │   ├── fonts.py           # Font installation
│       │   ├── shell.py           # Shell configuration
│       │   ├── cron.py            # Cron job management
│       │   └── installer.py       # Main orchestrator
│       ├── tmux/                   # Tmux theme management
│       │   ├── models.py          # Data models
│       │   ├── theme_manager.py   # Theme loading
│       │   └── theme_applier.py   # Theme application
│       ├── utils/                  # Utilities
│       │   ├── logger.py          # Logging configuration
│       │   ├── file_utils.py      # File operations
│       │   └── shell_utils.py     # Shell operations
│       └── data/
│           └── themes.yaml        # Theme database
├── tests/                          # Test suite
│   ├── conftest.py                # Pytest configuration
│   ├── test_utils/                # Utility tests
│   ├── test_installer/            # Installer tests
│   └── test_tmux/                 # Tmux tests
├── scripts/                        # Legacy scripts (still available)
├── dotfiles/                       # Dotfile templates
├── fonts/                          # Font files
├── pyproject.toml                  # Modern Python packaging
├── requirements.txt                # Dependencies
└── install.sh                      # Lightweight wrapper

```

## Installation

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/builderOfTheWorlds/environmentConfigurator/main/install.sh | bash
```

### Manual Install

```bash
# Clone the repository
git clone https://github.com/builderOfTheWorlds/environmentConfigurator.git
cd environmentConfigurator

# Install with pip (recommended: use virtual environment)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Or install system-wide
pip install --user -e .

# Run the installer
env-config install
```

### Test Mode

```bash
# Run in test mode to see what would happen without making changes
bash install.sh --test

# Or with the Python CLI
env-config install --test
```

## Commands

### Main Commands (`env-config`)

```bash
# Installation
env-config install                 # Install environment configuration
env-config install --test          # Test mode (dry run)
env-config install --no-fonts      # Skip font installation
env-config uninstall               # Remove environment configuration

# Status and Information
env-config status                  # Show installation status
env-config info                    # Show system information

# Help
env-config --help                  # Show all commands
```

### Theme Switcher (`tmux-theme-switcher`)

```bash
# List themes
tmux-theme-switcher list                    # List all themes
tmux-theme-switcher list -c green           # Filter by category
tmux-theme-switcher list -s "tokyo"         # Search themes

# View categories
tmux-theme-switcher categories              # List all categories

# Preview and apply themes
tmux-theme-switcher preview "Tokyo Night"   # Preview a theme
tmux-theme-switcher apply "Tokyo Night"     # Apply a theme
tmux-theme-switcher apply "Tokyo Night" -f  # Apply without confirmation

# Check current theme
tmux-theme-switcher current                 # Show current theme

# Statistics
tmux-theme-switcher stats                   # Show theme statistics

# Interactive mode (original TUI)
tmux-theme-switcher interactive             # Launch curses TUI
```

### Session Manager (`tmux-session-manager`)

```bash
# List and manage tmux sessions
tmux-session-manager list           # List all sessions
tmux-session-manager cleanup        # Clean up old backups
tmux-session-manager restore        # Restore a session

# See the original script for full options
tmux-session-manager --help
```

### Config Merger (`merge-shell-config`)

```bash
# Merge bash to zsh configuration
merge-shell-config                  # Merge ~/.bashrc to ~/.zshrc
merge-shell-config --dry-run        # Preview changes without applying
```

## Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/builderOfTheWorlds/environmentConfigurator.git
cd environmentConfigurator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/environment_configurator

# Run specific test file
pytest tests/test_utils/test_file_utils.py

# Run with verbose output
pytest -v

# Run and show coverage report
pytest --cov=src/environment_configurator --cov-report=html
# Then open htmlcov/index.html in a browser
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Type checking with mypy
mypy src/

# Lint with flake8
flake8 src/ tests/
```

## Architecture

### Modular Design

The refactored codebase follows these principles:

1. **Separation of Concerns** - Each module has a single, well-defined responsibility
2. **Dependency Injection** - Components receive dependencies rather than creating them
3. **Configuration Objects** - Settings passed via typed configuration classes
4. **Error Handling** - Comprehensive error handling with proper logging
5. **Type Safety** - Full type hints for better IDE support and error catching

### Logging

The logging system provides:

- **Multiple handlers** - Console and rotating file logs
- **Configurable levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Structured format** - Timestamps, module names, and log levels
- **Performance tracking** - Debug-level timing information
- **Log rotation** - Automatic rotation at 10MB with 5 backups

Logs are stored in: `~/.config/environment-configurator/logs/`

### Testing Strategy

Tests are organized by module:

- `test_utils/` - Utility function tests
- `test_installer/` - Installer component tests
- `test_tmux/` - Theme management tests

Fixtures in `conftest.py` provide:
- Temporary directories
- Mock home directories
- Sample configuration files

## Configuration Files

### Themes (`src/environment_configurator/data/themes.yaml`)

Themes are now in YAML format for easy customization:

```yaml
themes:
  - name: "My Custom Theme"
    category: "custom"
    description: "My awesome theme"
    bg_color: "#000000"
    fg_color: "#ffffff"
    accent_color: "#ff0000"
    # ... more colors
```

### Installer Config (`src/environment_configurator/installer/config.py`)

Installation settings can be customized programmatically or via CLI options.

## Migration from v1.x

The refactored version is backward compatible:

1. **Old Scripts Still Work** - Original scripts in `scripts/` directory remain functional
2. **Same Dotfiles** - Dotfile structure unchanged
3. **Same Installation Directory** - Still uses `~/.environment-config`
4. **Enhanced Features** - New CLI commands provide better UX

### Migrating

If you have v1.x installed:

```bash
# Update normally
cd ~/.environment-config
git pull origin main

# Reinstall with new structure
bash install.sh
```

## Troubleshooting

### Python Package Not Found

If you get "command not found" errors:

```bash
# Ensure the package is installed
pip install --user -e /path/to/environmentConfigurator

# Add ~/.local/bin to PATH (if using --user install)
export PATH="$HOME/.local/bin:$PATH"

# Or activate virtual environment
source ~/.environment-config/.venv/bin/activate
```

### Theme Application Issues

```bash
# Check current theme
tmux-theme-switcher current

# View logs
tail -f ~/.config/environment-configurator/logs/env_configurator_*.log

# Apply with verbose logging
env-config --verbose
```

### Installation Failures

```bash
# Run in test mode to see what would happen
bash install.sh --test

# Check Python version
python3 --version  # Should be 3.8 or higher

# Check dependencies
pip install -r requirements.txt
```

## Contributing

### Adding New Themes

1. Edit `src/environment_configurator/data/themes.yaml`
2. Add your theme following the existing format
3. Test with `tmux-theme-switcher list`
4. Submit a pull request

### Adding New Features

1. Create feature branch
2. Add tests in `tests/`
3. Implement feature in appropriate module
4. Update documentation
5. Run tests and code quality checks
6. Submit pull request

## License

MIT License - see LICENSE file for details

## Credits

- Original author: builderOfTheWorlds
- Refactored version: Enterprise-level Python refactoring
- Theme collections: Various open-source projects (Nord, Dracula, Catppuccin, etc.)

## Changelog

### v2.0.0 (Current)

- Complete refactor to modular Python project
- Added comprehensive test suite
- Modernized CLI with Click and Rich
- Extracted themes to YAML
- Enterprise-grade logging
- Type hints throughout
- Proper packaging with entry points

### v1.x (Legacy)

- Original bash-based implementation
- Python scripts for themes and utilities
- See `install.sh.old` for legacy installer
