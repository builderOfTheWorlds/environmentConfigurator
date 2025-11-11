#!/usr/bin/env python3
"""
Interactive Tmux Theme Switcher
A beautiful TUI for browsing and applying tmux themes with live preview.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import curses
from dataclasses import dataclass


@dataclass
class Theme:
    """Theme configuration"""
    name: str
    category: str
    description: str
    bg_color: str
    fg_color: str
    accent_color: str
    border_color: str
    border_active: str
    inactive_bg: str
    message_bg: str
    message_fg: str
    activity_color: str
    dir_color: str
    bat_theme: str
    ps1_color: str
    # Additional colors for preview
    color_swatches: Dict[str, str]  # name -> hex


# Theme Database - Categorized by primary color
THEMES = {
    "🟢 Green": [
        Theme(
            name="Matrix Green",
            category="green",
            description="Classic bright terminal green",
            bg_color="#000000",
            fg_color="#ccffcc",
            accent_color="#00ff00",
            border_color="#00aa00",
            border_active="#00ff00",
            inactive_bg="#1a1a1a",
            message_bg="#00ff00",
            message_fg="#000000",
            activity_color="#00ff00",
            dir_color="01;32",
            bat_theme="DarkNeon",
            ps1_color="\\[\\033[01;32m\\]",
            color_swatches={
                "BG": "#000000",
                "FG": "#ccffcc",
                "Accent": "#00ff00",
                "Border": "#00aa00",
            }
        ),
        Theme(
            name="Forest Green",
            category="green",
            description="Earthy, muted tones",
            bg_color="#1a1c19",
            fg_color="#a9c496",
            accent_color="#588157",
            border_color="#2d3325",
            border_active="#739372",
            inactive_bg="#232620",
            message_bg="#588157",
            message_fg="#1a1c19",
            activity_color="#88aa77",
            dir_color="01;38;5;108",
            bat_theme="Nord",
            ps1_color="\\[\\033[38;5;108m\\]",
            color_swatches={
                "BG": "#1a1c19",
                "FG": "#a9c496",
                "Accent": "#588157",
                "Border": "#739372",
            }
        ),
        Theme(
            name="Emerald",
            category="green",
            description="Rich, vibrant green",
            bg_color="#101816",
            fg_color="#d1fae5",
            accent_color="#34d399",
            border_color="#1f2f29",
            border_active="#6ee7b7",
            inactive_bg="#172320",
            message_bg="#34d399",
            message_fg="#101816",
            activity_color="#5de4a8",
            dir_color="01;38;5;79",
            bat_theme="Monokai Extended Bright",
            ps1_color="\\[\\033[38;5;79m\\]",
            color_swatches={
                "BG": "#101816",
                "FG": "#d1fae5",
                "Accent": "#34d399",
                "Border": "#6ee7b7",
            }
        ),
        Theme(
            name="Gruvbox Dark",
            category="green",
            description="Retro groove warm colors",
            bg_color="#282828",
            fg_color="#ebdbb2",
            accent_color="#b8bb26",
            border_color="#504945",
            border_active="#b8bb26",
            inactive_bg="#3c3836",
            message_bg="#b8bb26",
            message_fg="#282828",
            activity_color="#8ec07c",
            dir_color="01;38;5;142",
            bat_theme="gruvbox-dark",
            ps1_color="\\[\\033[38;5;142m\\]",
            color_swatches={
                "BG": "#282828",
                "FG": "#ebdbb2",
                "Green": "#b8bb26",
                "Aqua": "#8ec07c",
            }
        ),
        Theme(
            name="Dracula Green",
            category="green",
            description="Purple background with green accents",
            bg_color="#282a36",
            fg_color="#f8f8f2",
            accent_color="#50fa7b",
            border_color="#44475a",
            border_active="#8be9fd",
            inactive_bg="#343746",
            message_bg="#50fa7b",
            message_fg="#282a36",
            activity_color="#50fa7b",
            dir_color="01;38;5;84",
            bat_theme="Dracula",
            ps1_color="\\[\\033[38;5;84m\\]",
            color_swatches={
                "BG": "#282a36",
                "FG": "#f8f8f2",
                "Green": "#50fa7b",
                "Cyan": "#8be9fd",
            }
        ),
        Theme(
            name="Nord Aurora",
            category="green",
            description="Subtle green on dark background",
            bg_color="#2e3440",
            fg_color="#d8dee9",
            accent_color="#a3be8c",
            border_color="#3b4252",
            border_active="#88c0d0",
            inactive_bg="#3b4252",
            message_bg="#a3be8c",
            message_fg="#2e3440",
            activity_color="#88c0d0",
            dir_color="01;38;5;150",
            bat_theme="Nord",
            ps1_color="\\[\\033[38;5;150m\\]",
            color_swatches={
                "BG": "#2e3440",
                "FG": "#d8dee9",
                "Green": "#a3be8c",
                "Frost": "#88c0d0",
            }
        ),
    ],
    "🔵 Blue": [
        Theme(
            name="Gemini",
            category="blue",
            description="Blue and gray tones",
            bg_color="#1f2229",
            fg_color="#e1e1e1",
            accent_color="#4285f4",
            border_color="#4a4a4a",
            border_active="#4285f4",
            inactive_bg="#2d3037",
            message_bg="#4285f4",
            message_fg="#1f2229",
            activity_color="#8ab4f8",
            dir_color="01;34",
            bat_theme="OneHalfDark",
            ps1_color="\\[\\033[01;34m\\]",
            color_swatches={
                "BG": "#1f2229",
                "FG": "#e1e1e1",
                "Blue": "#4285f4",
                "Light Blue": "#8ab4f8",
            }
        ),
        Theme(
            name="Tokyo Night",
            category="blue",
            description="Downtown Tokyo lights at night",
            bg_color="#1a1b26",
            fg_color="#c0caf5",
            accent_color="#7aa2f7",
            border_color="#414868",
            border_active="#7aa2f7",
            inactive_bg="#16161e",
            message_bg="#7aa2f7",
            message_fg="#1a1b26",
            activity_color="#7dcfff",
            dir_color="01;38;5;111",
            bat_theme="OneHalfDark",
            ps1_color="\\[\\033[38;5;111m\\]",
            color_swatches={
                "BG": "#1a1b26",
                "FG": "#c0caf5",
                "Blue": "#7aa2f7",
                "Cyan": "#7dcfff",
            }
        ),
        Theme(
            name="Tokyo Night Storm",
            category="blue",
            description="Tokyo Night with lighter background",
            bg_color="#24283b",
            fg_color="#c0caf5",
            accent_color="#7aa2f7",
            border_color="#414868",
            border_active="#7aa2f7",
            inactive_bg="#1f2335",
            message_bg="#7aa2f7",
            message_fg="#24283b",
            activity_color="#7dcfff",
            dir_color="01;38;5;111",
            bat_theme="OneHalfDark",
            ps1_color="\\[\\033[38;5;111m\\]",
            color_swatches={
                "BG": "#24283b",
                "FG": "#c0caf5",
                "Blue": "#7aa2f7",
                "Cyan": "#7dcfff",
            }
        ),
        Theme(
            name="Solarized Dark",
            category="blue",
            description="Precision colors by Ethan Schoonover",
            bg_color="#002b36",
            fg_color="#839496",
            accent_color="#268bd2",
            border_color="#073642",
            border_active="#268bd2",
            inactive_bg="#073642",
            message_bg="#268bd2",
            message_fg="#002b36",
            activity_color="#2aa198",
            dir_color="01;38;5;33",
            bat_theme="Solarized (dark)",
            ps1_color="\\[\\033[38;5;33m\\]",
            color_swatches={
                "BG": "#002b36",
                "FG": "#839496",
                "Blue": "#268bd2",
                "Cyan": "#2aa198",
            }
        ),
    ],
    "🟣 Purple": [
        Theme(
            name="Purple Dream",
            category="purple",
            description="Vibrant purple and magenta",
            bg_color="#1a0d2e",
            fg_color="#e0c3fc",
            accent_color="#b565d8",
            border_color="#3d2b5c",
            border_active="#d896ff",
            inactive_bg="#251640",
            message_bg="#b565d8",
            message_fg="#1a0d2e",
            activity_color="#d896ff",
            dir_color="01;35",
            bat_theme="Dracula",
            ps1_color="\\[\\033[01;35m\\]",
            color_swatches={
                "BG": "#1a0d2e",
                "FG": "#e0c3fc",
                "Purple": "#b565d8",
                "Magenta": "#d896ff",
            }
        ),
        Theme(
            name="Catppuccin Mocha",
            category="purple",
            description="Soothing pastel theme - Mocha variant",
            bg_color="#1e1e2e",
            fg_color="#cdd6f4",
            accent_color="#cba6f7",
            border_color="#313244",
            border_active="#cba6f7",
            inactive_bg="#181825",
            message_bg="#cba6f7",
            message_fg="#1e1e2e",
            activity_color="#f5c2e7",
            dir_color="01;38;5;183",
            bat_theme="Catppuccin-mocha",
            ps1_color="\\[\\033[38;5;183m\\]",
            color_swatches={
                "BG": "#1e1e2e",
                "FG": "#cdd6f4",
                "Mauve": "#cba6f7",
                "Pink": "#f5c2e7",
            }
        ),
        Theme(
            name="Kanagawa Wave",
            category="purple",
            description="Inspired by Hokusai's Great Wave",
            bg_color="#1f1f28",
            fg_color="#dcd7ba",
            accent_color="#957fb8",
            border_color="#2a2a37",
            border_active="#7e9cd8",
            inactive_bg="#16161d",
            message_bg="#957fb8",
            message_fg="#1f1f28",
            activity_color="#7fb4ca",
            dir_color="01;38;5;146",
            bat_theme="Nord",
            ps1_color="\\[\\033[38;5;146m\\]",
            color_swatches={
                "BG": "#1f1f28",
                "FG": "#dcd7ba",
                "Violet": "#957fb8",
                "Blue": "#7e9cd8",
            }
        ),
    ],
    "🌸 Pink/Rose": [
        Theme(
            name="Rose Pine",
            category="pink",
            description="All natural pine, faux fur and soho vibes",
            bg_color="#191724",
            fg_color="#e0def4",
            accent_color="#eb6f92",
            border_color="#26233a",
            border_active="#eb6f92",
            inactive_bg="#1f1d2e",
            message_bg="#eb6f92",
            message_fg="#191724",
            activity_color="#ebbcba",
            dir_color="01;38;5;211",
            bat_theme="Nord",
            ps1_color="\\[\\033[38;5;211m\\]",
            color_swatches={
                "BG": "#191724",
                "FG": "#e0def4",
                "Love": "#eb6f92",
                "Rose": "#ebbcba",
            }
        ),
        Theme(
            name="Rose Pine Moon",
            category="pink",
            description="Rose Pine with moon-inspired palette",
            bg_color="#232136",
            fg_color="#e0def4",
            accent_color="#eb6f92",
            border_color="#393552",
            border_active="#eb6f92",
            inactive_bg="#2a273f",
            message_bg="#eb6f92",
            message_fg="#232136",
            activity_color="#ea9a97",
            dir_color="01;38;5;211",
            bat_theme="Nord",
            ps1_color="\\[\\033[38;5;211m\\]",
            color_swatches={
                "BG": "#232136",
                "FG": "#e0def4",
                "Love": "#eb6f92",
                "Rose": "#ea9a97",
            }
        ),
    ],
    "🟠 Orange/Warm": [
        Theme(
            name="Monokai Pro",
            category="orange",
            description="Modern take on classic Monokai",
            bg_color="#2d2a2e",
            fg_color="#fcfcfa",
            accent_color="#ff6188",
            border_color="#423f42",
            border_active="#ff6188",
            inactive_bg="#221f22",
            message_bg="#ff6188",
            message_fg="#2d2a2e",
            activity_color="#ffd866",
            dir_color="01;38;5;204",
            bat_theme="Monokai Extended",
            ps1_color="\\[\\033[38;5;204m\\]",
            color_swatches={
                "BG": "#2d2a2e",
                "FG": "#fcfcfa",
                "Red": "#ff6188",
                "Yellow": "#ffd866",
            }
        ),
        Theme(
            name="Gruvbox Light",
            category="orange",
            description="Retro groove warm colors (light)",
            bg_color="#fbf1c7",
            fg_color="#3c3836",
            accent_color="#d65d0e",
            border_color="#ebdbb2",
            border_active="#d65d0e",
            inactive_bg="#ebdbb2",
            message_bg="#d65d0e",
            message_fg="#fbf1c7",
            activity_color="#b57614",
            dir_color="01;38;5;172",
            bat_theme="gruvbox-light",
            ps1_color="\\[\\033[38;5;172m\\]",
            color_swatches={
                "BG": "#fbf1c7",
                "FG": "#3c3836",
                "Orange": "#d65d0e",
                "Yellow": "#b57614",
            }
        ),
    ],
    "🟦 Cyan/Teal": [
        Theme(
            name="Mint/Teal",
            category="cyan",
            description="Modern, lighter cyan-green",
            bg_color="#161b22",
            fg_color="#afebdc",
            accent_color="#2ed5b6",
            border_color="#233732",
            border_active="#40c4a9",
            inactive_bg="#1c2128",
            message_bg="#2ed5b6",
            message_fg="#161b22",
            activity_color="#58d9c0",
            dir_color="01;36",
            bat_theme="Monokai Extended",
            ps1_color="\\[\\033[01;36m\\]",
            color_swatches={
                "BG": "#161b22",
                "FG": "#afebdc",
                "Teal": "#2ed5b6",
                "Cyan": "#40c4a9",
            }
        ),
    ],
    "⚪ Neutral/Light": [
        Theme(
            name="Solarized Light",
            category="light",
            description="Precision colors (light mode)",
            bg_color="#fdf6e3",
            fg_color="#657b83",
            accent_color="#268bd2",
            border_color="#eee8d5",
            border_active="#268bd2",
            inactive_bg="#eee8d5",
            message_bg="#268bd2",
            message_fg="#fdf6e3",
            activity_color="#2aa198",
            dir_color="01;38;5;33",
            bat_theme="Solarized (light)",
            ps1_color="\\[\\033[38;5;33m\\]",
            color_swatches={
                "BG": "#fdf6e3",
                "FG": "#657b83",
                "Blue": "#268bd2",
                "Cyan": "#2aa198",
            }
        ),
        Theme(
            name="Catppuccin Latte",
            category="light",
            description="Soothing pastel theme - Latte variant (light)",
            bg_color="#eff1f5",
            fg_color="#4c4f69",
            accent_color="#8839ef",
            border_color="#ccd0da",
            border_active="#8839ef",
            inactive_bg="#e6e9ef",
            message_bg="#8839ef",
            message_fg="#eff1f5",
            activity_color="#ea76cb",
            dir_color="01;38;5;98",
            bat_theme="Catppuccin-latte",
            ps1_color="\\[\\033[38;5;98m\\]",
            color_swatches={
                "BG": "#eff1f5",
                "FG": "#4c4f69",
                "Mauve": "#8839ef",
                "Pink": "#ea76cb",
            }
        ),
    ],
}


def get_all_themes() -> List[Tuple[str, Theme]]:
    """Get all themes as a flat list with their categories"""
    themes = []
    for category, theme_list in THEMES.items():
        for theme in theme_list:
            themes.append((category, theme))
    return themes


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_curses(r: int, g: int, b: int) -> Tuple[int, int, int]:
    """Convert RGB (0-255) to curses color range (0-1000)"""
    return int(r * 1000 / 255), int(g * 1000 / 255), int(b * 1000 / 255)


class ThemeSwitcher:
    """Interactive theme switcher with TUI"""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_idx = 0
        self.themes = get_all_themes()
        self.scroll_offset = 0
        self.color_pairs = {}

        # Initialize curses settings
        curses.curs_set(0)  # Hide cursor
        curses.use_default_colors()

        # Initialize colors if terminal supports it
        if curses.has_colors():
            curses.start_color()
            self.init_colors()

    def init_colors(self):
        """Initialize color pairs for the TUI"""
        # Basic color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)    # Headers
        curses.init_pair(2, curses.COLOR_CYAN, -1)     # Selected item
        curses.init_pair(3, curses.COLOR_WHITE, -1)    # Normal text
        curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Category
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Accent
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Selected bg

    def draw_header(self):
        """Draw the header"""
        height, width = self.stdscr.getmaxyx()

        # Title
        title = "🎨 TMUX THEME SWITCHER"
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(0, (width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Instructions
        instructions = "↑↓: Navigate | Enter: Apply | Q: Quit"
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(1, (width - len(instructions)) // 2, instructions)
        self.stdscr.attroff(curses.color_pair(3))

        # Separator
        self.stdscr.addstr(2, 0, "═" * width)

    def draw_theme_list(self, start_row: int, end_row: int, col: int, width: int):
        """Draw the theme list on the left side"""
        visible_height = end_row - start_row

        # Calculate scroll offset
        if self.current_idx < self.scroll_offset:
            self.scroll_offset = self.current_idx
        elif self.current_idx >= self.scroll_offset + visible_height:
            self.scroll_offset = self.current_idx - visible_height + 1

        # Draw themes
        row = start_row
        last_category = None
        idx = 0

        for category, theme in self.themes:
            if idx < self.scroll_offset:
                idx += 1
                continue
            if row >= end_row:
                break

            # Draw category header if new category
            if category != last_category:
                if row < end_row:
                    self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                    # Add extra space after category name and pad to full width for alignment
                    category_text = f" {category} ".ljust(width - 2)
                    self.stdscr.addstr(row, col, category_text)
                    self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                    row += 1
                    last_category = category

            if row >= end_row:
                break

            # Draw theme name
            is_selected = (idx == self.current_idx)
            prefix = "▶ " if is_selected else "  "

            if is_selected:
                self.stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(3))

            theme_text = f"{prefix}{theme.name}"
            if len(theme_text) > width - 2:
                theme_text = theme_text[:width-5] + "..."

            self.stdscr.addstr(row, col, theme_text.ljust(width - 2))

            if is_selected:
                self.stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.attroff(curses.color_pair(3))

            row += 1
            idx += 1

    def draw_preview(self, start_row: int, end_row: int, col: int, width: int):
        """Draw the theme preview on the right side"""
        _, theme = self.themes[self.current_idx]

        row = start_row

        # Theme name and description
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(row, col, f"📦 {theme.name}")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        row += 1

        self.stdscr.attron(curses.color_pair(3))
        desc = theme.description
        if len(desc) > width - 2:
            desc = desc[:width-5] + "..."
        self.stdscr.addstr(row, col, desc)
        self.stdscr.attroff(curses.color_pair(3))
        row += 2

        # Color swatches
        self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(row, col, "🎨 Color Palette:")
        self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
        row += 1

        for name, hex_color in theme.color_swatches.items():
            if row >= end_row - 15:
                break
            swatch = f"  ■ {name:12} {hex_color}"
            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(row, col, swatch)
            self.stdscr.attroff(curses.color_pair(3))
            row += 1

        row += 1

        # Mock tmux status bar with theme colors
        if row + 5 < end_row:
            self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            self.stdscr.addstr(row, col, "📊 Tmux Status Bar Preview:")
            self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            row += 1

            bar_width = min(width - 4, 50)

            # Show a colorful representation using the theme description
            # Top border in border color style
            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(row, col, "┌" + "─" * bar_width + "┐")
            self.stdscr.attroff(curses.color_pair(3))
            row += 1

            # Status bar content with color indicators
            # Left part (accent color) - session name
            status_left = "[Session]"
            # Middle part (normal) - window list
            status_middle = " 1:bash"
            # Active window (accent/highlight)
            status_active = "*"
            # More windows
            status_more = " 2:vim "
            # Right part (normal) - time
            status_right = datetime.now().strftime('%H:%M')

            # Calculate padding
            used = len(status_left) + len(status_middle) + len(status_active) + len(status_more) + len(status_right) + 1
            padding = max(0, bar_width - used)

            # Draw the status line with visual color indicators
            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(row, col, "│")
            self.stdscr.attroff(curses.color_pair(3))

            # Session in accent color
            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(status_left)
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

            # Regular window
            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(status_middle)
            self.stdscr.attroff(curses.color_pair(3))

            # Active window indicator (highlighted)
            self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
            self.stdscr.addstr(status_active)
            self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)

            # More windows
            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(status_more)
            # Padding
            self.stdscr.addstr(" " * padding)
            # Time
            self.stdscr.addstr(status_right)
            self.stdscr.addstr("│")
            self.stdscr.attroff(curses.color_pair(3))
            row += 1

            # Bottom border
            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(row, col, "└" + "─" * bar_width + "┘")
            self.stdscr.attroff(curses.color_pair(3))
            row += 1

            # Add color legend
            self.stdscr.attron(curses.color_pair(3))
            legend = "  (Colors: "
            self.stdscr.addstr(row, col, legend)
            self.stdscr.attroff(curses.color_pair(3))

            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr("accent")
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(", ")
            self.stdscr.attroff(curses.color_pair(3))

            self.stdscr.attron(curses.color_pair(2) | curses.A_REVERSE)
            self.stdscr.addstr("active")
            self.stdscr.attroff(curses.color_pair(2) | curses.A_REVERSE)

            self.stdscr.attron(curses.color_pair(3))
            self.stdscr.addstr(")")
            self.stdscr.attroff(curses.color_pair(3))
            row += 2

        # Directory listing preview (eza -l -T --level 2 style)
        if row + 10 < end_row:
            self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            self.stdscr.addstr(row, col, "📁 Directory Listing (eza -l -T --level 2):")
            self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            row += 1

            # Simulate directory tree with colored directories
            listing = [
                ("drwxr-xr-x  4 user group  4.0K  ", "projects", "/", True),
                ("├──", "drwxr-xr-x  2 user group  4.0K  ", "frontend", "/", True),
                ("│  ├──", "-rw-r--r--  1 user group  1.2K  ", "index.html", "", False),
                ("│  └──", "-rw-r--r--  1 user group  3.4K  ", "style.css", "", False),
                ("├──", "drwxr-xr-x  2 user group  4.0K  ", "backend", "/", True),
                ("│  ├──", "-rw-r--r--  1 user group  5.6K  ", "server.py", "", False),
                ("│  └──", "-rw-r--r--  1 user group   890  ", "config.json", "", False),
                ("└──", "drwxr-xr-x  2 user group  4.0K  ", "docs", "/", True),
                ("   ├──", "-rw-r--r--  1 user group  2.1K  ", "README.md", "", False),
                ("   └──", "-rw-r--r--  1 user group  1.5K  ", "GUIDE.md", "", False),
            ]

            for item in listing:
                if row >= end_row:
                    break

                # Handle different tuple lengths
                if len(item) == 5:
                    tree, perms, name, suffix, is_dir = item
                    self.stdscr.attron(curses.color_pair(3))
                    self.stdscr.addstr(row, col, f"  {tree} ")
                    self.stdscr.addstr(perms)
                    self.stdscr.attroff(curses.color_pair(3))

                    # Color the name based on whether it's a directory
                    if is_dir:
                        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                    else:
                        self.stdscr.attron(curses.color_pair(3))

                    self.stdscr.addstr(name + suffix)

                    if is_dir:
                        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                    else:
                        self.stdscr.attroff(curses.color_pair(3))
                else:
                    # Simple line (header)
                    perms, name, suffix, is_dir = item
                    self.stdscr.attron(curses.color_pair(3))
                    self.stdscr.addstr(row, col, f"  {perms}")
                    self.stdscr.attroff(curses.color_pair(3))

                    if is_dir:
                        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                    else:
                        self.stdscr.attron(curses.color_pair(3))

                    self.stdscr.addstr(name + suffix)

                    if is_dir:
                        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                    else:
                        self.stdscr.attroff(curses.color_pair(3))

                row += 1

            # Add color note
            if row < end_row:
                self.stdscr.attron(curses.color_pair(3))
                note = f"  (Directories shown in "
                self.stdscr.addstr(row, col, note)
                self.stdscr.attroff(curses.color_pair(3))

                self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.addstr("theme color")
                self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

                self.stdscr.attron(curses.color_pair(3))
                self.stdscr.addstr(")")
                self.stdscr.attroff(curses.color_pair(3))

    def draw_footer(self):
        """Draw the footer with apply button"""
        height, width = self.stdscr.getmaxyx()

        # Separator
        self.stdscr.addstr(height - 3, 0, "═" * width)

        # Footer text
        footer = "Press ENTER to apply this theme (backups will be created)"
        self.stdscr.attron(curses.color_pair(5))
        self.stdscr.addstr(height - 2, (width - len(footer)) // 2, footer)
        self.stdscr.attroff(curses.color_pair(5))

    def draw(self):
        """Draw the entire UI"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Draw header
        self.draw_header()

        # Calculate split layout
        split_col = width // 3
        content_start = 3
        content_end = height - 3

        # Draw vertical separator
        for i in range(content_start, content_end):
            self.stdscr.addstr(i, split_col, "│")

        # Draw theme list (left side)
        self.draw_theme_list(content_start, content_end, 0, split_col)

        # Draw preview (right side)
        self.draw_preview(content_start, content_end, split_col + 2, width - split_col - 2)

        # Draw footer
        self.draw_footer()

        self.stdscr.refresh()

    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False to quit."""
        key = self.stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            return False
        elif key == curses.KEY_UP:
            if self.current_idx > 0:
                self.current_idx -= 1
        elif key == curses.KEY_DOWN:
            if self.current_idx < len(self.themes) - 1:
                self.current_idx += 1
        elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
            # Apply theme
            _, theme = self.themes[self.current_idx]
            self.apply_theme(theme)

        return True

    def apply_theme(self, theme: Theme):
        """Apply the selected theme (with backup)"""
        # Show confirmation
        height, width = self.stdscr.getmaxyx()

        # Clear a space for the dialog
        dialog_height = 10
        dialog_width = 60
        start_row = (height - dialog_height) // 2
        start_col = (width - dialog_width) // 2

        # Draw dialog box
        for i in range(dialog_height):
            self.stdscr.addstr(start_row + i, start_col, " " * dialog_width)

        # Draw border
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(start_row, start_col, "┌" + "─" * (dialog_width - 2) + "┐")
        for i in range(1, dialog_height - 1):
            self.stdscr.addstr(start_row + i, start_col, "│")
            self.stdscr.addstr(start_row + i, start_col + dialog_width - 1, "│")
        self.stdscr.addstr(start_row + dialog_height - 1, start_col, "└" + "─" * (dialog_width - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Dialog content
        self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        title = f"Apply Theme: {theme.name}"
        self.stdscr.addstr(start_row + 2, start_col + (dialog_width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        self.stdscr.attron(curses.color_pair(3))
        msg1 = "This will backup and modify:"
        self.stdscr.addstr(start_row + 4, start_col + (dialog_width - len(msg1)) // 2, msg1)
        msg2 = "• ~/.tmux.conf"
        self.stdscr.addstr(start_row + 5, start_col + (dialog_width - len(msg2)) // 2, msg2)
        msg3 = "• ~/.zshrc or ~/.bashrc"
        self.stdscr.addstr(start_row + 6, start_col + (dialog_width - len(msg3)) // 2, msg3)
        self.stdscr.attroff(curses.color_pair(3))

        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        prompt = "Press ENTER to confirm, ESC to cancel"
        self.stdscr.addstr(start_row + 8, start_col + (dialog_width - len(prompt)) // 2, prompt)
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        self.stdscr.refresh()

        # Wait for confirmation
        while True:
            key = self.stdscr.getch()
            if key == 27:  # ESC
                return
            elif key == ord('\n') or key == 10:
                break

        # Perform the actual application
        try:
            self.perform_theme_application(theme)

            # Show success message
            for i in range(dialog_height):
                self.stdscr.addstr(start_row + i, start_col, " " * dialog_width)

            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            success = "✓ Theme Applied Successfully!"
            self.stdscr.addstr(start_row + 4, start_col + (dialog_width - len(success)) // 2, success)
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

            self.stdscr.attron(curses.color_pair(3))
            info = "Press any key to continue..."
            self.stdscr.addstr(start_row + 6, start_col + (dialog_width - len(info)) // 2, info)
            self.stdscr.attroff(curses.color_pair(3))

            self.stdscr.refresh()
            self.stdscr.getch()

        except Exception as e:
            # Show error message
            for i in range(dialog_height):
                self.stdscr.addstr(start_row + i, start_col, " " * dialog_width)

            self.stdscr.attron(curses.color_pair(1))
            error = "✗ Error Applying Theme"
            self.stdscr.addstr(start_row + 4, start_col + (dialog_width - len(error)) // 2, error)
            self.stdscr.attroff(curses.color_pair(1))

            self.stdscr.attron(curses.color_pair(3))
            err_msg = str(e)[:dialog_width-4]
            self.stdscr.addstr(start_row + 5, start_col + 2, err_msg)
            info = "Press any key to continue..."
            self.stdscr.addstr(start_row + 7, start_col + (dialog_width - len(info)) // 2, info)
            self.stdscr.attroff(curses.color_pair(3))

            self.stdscr.refresh()
            self.stdscr.getch()

    def perform_theme_application(self, theme: Theme):
        """Perform the actual theme application with backups"""
        home = Path.home()
        tmux_conf = home / ".tmux.conf"

        # Detect shell
        shell = os.environ.get('SHELL', '/bin/bash')
        if 'zsh' in shell:
            shell_rc = home / ".zshrc"
        else:
            shell_rc = home / ".bashrc"

        # Create backups with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Backup tmux.conf
        if tmux_conf.exists():
            backup_path = home / f".tmux.conf.backup.{timestamp}"
            shutil.copy2(tmux_conf, backup_path)

        # Backup shell rc
        if shell_rc.exists():
            backup_path = home / f"{shell_rc.name}.backup.{timestamp}"
            shutil.copy2(shell_rc, backup_path)

        # Apply tmux theme
        self.apply_tmux_theme(tmux_conf, theme)

        # Apply shell theme
        self.apply_shell_theme(shell_rc, theme)

        # Reload tmux if running
        try:
            subprocess.run(["tmux", "source-file", str(tmux_conf)],
                         stderr=subprocess.DEVNULL, check=False)
            subprocess.run(["tmux", "display-message", f"Theme '{theme.name}' loaded!"],
                         stderr=subprocess.DEVNULL, check=False)
        except:
            pass

    def apply_tmux_theme(self, tmux_conf: Path, theme: Theme):
        """Apply theme to tmux.conf"""
        # Create theme block
        theme_block = f"""
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

        # Read current config
        if tmux_conf.exists():
            with open(tmux_conf, 'r') as f:
                content = f.read()

            # Remove old theme block if exists
            import re
            pattern = r'# ========================================\n# Theme:.*?\n# ========================================.*?# ========================================'
            content = re.sub(pattern, '', content, flags=re.DOTALL)

            # Append new theme
            with open(tmux_conf, 'w') as f:
                f.write(content.rstrip() + '\n' + theme_block)
        else:
            # Create new config with theme
            with open(tmux_conf, 'w') as f:
                f.write(theme_block)

    def apply_shell_theme(self, shell_rc: Path, theme: Theme):
        """Apply theme to shell rc file"""
        shell_block = f"""
# ======================================== TMUX THEME COLORS
# Auto-generated by tmux-theme-switcher.py
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

        if shell_rc.exists():
            with open(shell_rc, 'r') as f:
                content = f.read()

            # Remove old theme block
            import re
            pattern = r'# ======================================== TMUX THEME COLORS.*?# ======================================== END TMUX THEME COLORS\n'
            content = re.sub(pattern, '', content, flags=re.DOTALL)

            # Append new theme
            with open(shell_rc, 'w') as f:
                f.write(content.rstrip() + '\n' + shell_block)
        else:
            with open(shell_rc, 'w') as f:
                f.write(shell_block)

    def run(self):
        """Main loop"""
        while True:
            self.draw()
            if not self.handle_input():
                break


def main(stdscr):
    """Main entry point for curses"""
    switcher = ThemeSwitcher(stdscr)
    switcher.run()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nTheme switcher cancelled.")
        sys.exit(0)
