"""
Theme application for tmux and shell.

Handles applying themes to tmux configuration and shell RC files.
"""

import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.file_utils import backup_file, read_file, safe_write_file
from environment_configurator.utils.shell_utils import detect_shell, get_shell_rc_path
from environment_configurator.tmux.models import Theme

logger = get_logger(__name__)


class ThemeApplier:
    """Applies themes to tmux and shell configurations."""

    def __init__(self, backup_enabled: bool = True):
        """
        Initialize the theme applier.

        Args:
            backup_enabled: Whether to create backups before applying themes
        """
        self.backup_enabled = backup_enabled

    def apply_theme(self, theme: Theme) -> bool:
        """
        Apply a theme to both tmux and shell configurations.

        Args:
            theme: The theme to apply

        Returns:
            True if application successful, False otherwise
        """
        logger.info(f"Applying theme: {theme.name}")

        try:
            # Apply to tmux
            if not self.apply_tmux_theme(theme):
                logger.error("Failed to apply tmux theme")
                return False

            # Apply to shell
            if not self.apply_shell_theme(theme):
                logger.error("Failed to apply shell theme")
                return False

            # Reload tmux if running
            self.reload_tmux(theme)

            logger.info(f"Theme '{theme.name}' applied successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")
            return False

    def apply_tmux_theme(self, theme: Theme) -> bool:
        """
        Apply theme to tmux configuration.

        Args:
            theme: The theme to apply

        Returns:
            True if successful, False otherwise
        """
        home = Path.home()
        tmux_conf = home / ".tmux.conf"

        logger.debug(f"Applying tmux theme to: {tmux_conf}")

        # Backup existing file
        if self.backup_enabled and tmux_conf.exists():
            try:
                backup_file(tmux_conf)
            except Exception as e:
                logger.warning(f"Failed to backup tmux.conf: {e}")

        # Create theme block
        theme_block = self._generate_tmux_config(theme)

        # Read current config or start fresh
        if tmux_conf.exists():
            content = read_file(tmux_conf)

            # Remove old theme block
            pattern = (
                r"# ========================================\n"
                r"# Theme:.*?\n"
                r"# ========================================.*?"
                r"# ========================================"
            )
            content = re.sub(pattern, "", content, flags=re.DOTALL)

            # Append new theme
            content = content.rstrip() + "\n" + theme_block
        else:
            content = theme_block

        # Write config
        try:
            safe_write_file(tmux_conf, content, backup=False)
            logger.info(f"Applied tmux theme: {theme.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to write tmux config: {e}")
            return False

    def apply_shell_theme(self, theme: Theme) -> bool:
        """
        Apply theme to shell configuration.

        Args:
            theme: The theme to apply

        Returns:
            True if successful, False otherwise
        """
        shell_rc = get_shell_rc_path()

        logger.debug(f"Applying shell theme to: {shell_rc}")

        # Backup existing file
        if self.backup_enabled and shell_rc.exists():
            try:
                backup_file(shell_rc)
            except Exception as e:
                logger.warning(f"Failed to backup shell RC: {e}")

        # Create theme block
        theme_block = self._generate_shell_config(theme)

        # Read current config or start fresh
        if shell_rc.exists():
            content = read_file(shell_rc)

            # Remove old theme block
            pattern = (
                r"# ======================================== TMUX THEME COLORS.*?"
                r"# ======================================== END TMUX THEME COLORS\n"
            )
            content = re.sub(pattern, "", content, flags=re.DOTALL)

            # Append new theme
            content = content.rstrip() + "\n" + theme_block
        else:
            content = theme_block

        # Write config
        try:
            safe_write_file(shell_rc, content, backup=False)
            logger.info(f"Applied shell theme: {theme.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to write shell config: {e}")
            return False

    def _generate_tmux_config(self, theme: Theme) -> str:
        """
        Generate tmux configuration block for a theme.

        Args:
            theme: The theme to generate config for

        Returns:
            Tmux configuration string
        """
        return f"""
# ========================================
# Theme: {theme.name}
# ========================================

# Status bar colors
set -g status-style bg={theme.bg_color},fg={theme.fg_color}
set -g status-left-style bg={theme.bg_color},fg={theme.accent_color}
set -g status-right-style bg={theme.bg_color},fg={theme.fg_color}

# Pane border colors
set -g pane-border-style fg={theme.border_color}
set -g pane-active-border-style fg={theme.border_active}

# Window status colors
setw -g window-status-style fg={theme.fg_color},bg={theme.bg_color}
setw -g window-status-current-style fg={theme.bg_color},bg={theme.accent_color},bold

# Message colors
set -g message-style bg={theme.message_bg},fg={theme.message_fg},bold
set -g message-command-style bg={theme.message_bg},fg={theme.message_fg},bold

# Activity color
setw -g window-status-activity-style fg={theme.activity_color},bg={theme.bg_color}

# ========================================
"""

    def _generate_shell_config(self, theme: Theme) -> str:
        """
        Generate shell configuration block for a theme.

        Args:
            theme: The theme to generate config for

        Returns:
            Shell configuration string
        """
        return f"""
# ======================================== TMUX THEME COLORS
# Auto-generated by environment configurator
# Theme: {theme.name}
# ========================================

# EZA color configuration (for directory colors)
export EZA_COLORS="di={theme.dir_color}:ln=01;36:so=01;35:pi=40;33:ex={theme.dir_color}:bd=40;33;01:cd=40;33;01:su=37;41:sg=30;43:tw=30;42:ow={theme.dir_color}:uu={theme.dir_color}:gu={theme.dir_color}"

# Traditional LS_COLORS (fallback for standard ls command)
export LS_COLORS="di={theme.dir_color}:ln=01;36:so=01;35:pi=40;33:ex={theme.dir_color}:bd=40;33;01:cd=40;33;01:su=37;41:sg=30;43:tw=30;42:ow={theme.dir_color}"

# Bat theme (syntax highlighting)
export BAT_THEME="{theme.bat_theme}"

# FZF colors (matching theme)
export FZF_DEFAULT_OPTS="--color=fg:-1,bg:-1,hl:{theme.dir_color},fg+:#ffffff,bg+:#3a3a3a,hl+:{theme.dir_color} --color=info:{theme.dir_color},prompt:{theme.dir_color},pointer:{theme.dir_color},marker:{theme.dir_color},spinner:{theme.dir_color}"

# PS1 Configuration
export PS1="{theme.ps1_color}\\u\\[\\033[00m\\]@\\h:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ "

# Alias ll to eza -l
alias ll='eza -l'

# Alias llt to eza -l -T --level 2 -a
alias llt='eza -l -T --level 2 -a'

# ======================================== END TMUX THEME COLORS
"""

    def reload_tmux(self, theme: Theme) -> None:
        """
        Reload tmux configuration if tmux is running.

        Args:
            theme: The theme that was applied
        """
        try:
            # Try to source the config
            subprocess.run(
                ["tmux", "source-file", str(Path.home() / ".tmux.conf")],
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=5,
            )

            # Try to show a message
            subprocess.run(
                ["tmux", "display-message", f"Theme '{theme.name}' loaded!"],
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=5,
            )

            logger.debug("Tmux configuration reloaded")

        except Exception as e:
            logger.debug(f"Could not reload tmux (may not be running): {e}")

    def get_current_theme_name(self) -> Optional[str]:
        """
        Get the name of the currently applied theme.

        Returns:
            Theme name or None if no theme is applied
        """
        tmux_conf = Path.home() / ".tmux.conf"

        if not tmux_conf.exists():
            return None

        try:
            content = read_file(tmux_conf)

            # Look for theme comment
            match = re.search(r"# Theme: (.+)", content)
            if match:
                return match.group(1)

        except Exception as e:
            logger.error(f"Failed to read current theme: {e}")

        return None
