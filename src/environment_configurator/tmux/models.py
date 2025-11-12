"""
Data models for tmux themes.

Provides strongly-typed models for theme configuration.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ThemeCategory:
    """Represents a theme category."""

    id: str
    display_name: str
    description: str


@dataclass
class Theme:
    """Represents a tmux theme configuration."""

    name: str
    category: str
    description: str

    # Color configuration
    bg_color: str
    fg_color: str
    accent_color: str
    border_color: str
    border_active: str
    inactive_bg: str
    message_bg: str
    message_fg: str
    activity_color: str

    # Shell and tool configuration
    dir_color: str
    bat_theme: str
    ps1_color: str

    # Additional metadata
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, str]:
        """Convert theme to dictionary for easier serialization."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "bg_color": self.bg_color,
            "fg_color": self.fg_color,
            "accent_color": self.accent_color,
            "border_color": self.border_color,
            "border_active": self.border_active,
            "inactive_bg": self.inactive_bg,
            "message_bg": self.message_bg,
            "message_fg": self.message_fg,
            "activity_color": self.activity_color,
            "dir_color": self.dir_color,
            "bat_theme": self.bat_theme,
            "ps1_color": self.ps1_color,
        }

    def get_color_swatches(self) -> Dict[str, str]:
        """
        Get a dictionary of color swatches for preview.

        Returns:
            Dictionary mapping color names to hex values
        """
        return {
            "BG": self.bg_color,
            "FG": self.fg_color,
            "Accent": self.accent_color,
            "Border": self.border_active,
        }

    def __str__(self) -> str:
        """String representation of theme."""
        return f"{self.name} ({self.category})"
