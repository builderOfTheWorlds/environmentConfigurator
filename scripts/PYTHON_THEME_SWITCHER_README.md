# 🎨 Interactive Tmux Theme Switcher (Python)

A beautiful, interactive terminal user interface for browsing and applying tmux themes with live preview.

## ✨ Features

- **🖼️ Interactive TUI** - Split-screen interface with theme list and live preview
- **⌨️ Arrow Key Navigation** - Smooth browsing through 25+ themes
- **🎨 Live Preview** - See color swatches, mock tmux bar, and code samples
- **🗂️ Categorized Themes** - Organized by primary color (Green, Blue, Purple, Pink/Rose, Orange/Warm, Cyan/Teal, Neutral/Light)
- **💾 Automatic Backups** - Creates timestamped backups before applying changes
- **🔄 Instant Application** - Applies themes to tmux and shell with confirmation
- **🎭 Popular Themes** - Includes Catppuccin, Tokyo Night, Gruvbox, Solarized, Monokai Pro, Rose Pine, Kanagawa, and more!

## 📋 Requirements

- Python 3.6+
- tmux
- A terminal with color support (256 colors recommended)

The script uses only Python standard library modules:
- `curses` - for the TUI (included with Python on Linux/macOS)
- `os`, `sys`, `shutil`, `subprocess`, `pathlib`, `datetime`, `dataclasses` - all standard library

## 🚀 Installation

The script is already executable and ready to use:

```bash
# Run from anywhere
/home/user/environmentConfigurator/scripts/tmux-theme-switcher.py

# Or add to your PATH for easy access
```

## 📖 Usage

### Starting the Theme Switcher

```bash
python3 /home/user/environmentConfigurator/scripts/tmux-theme-switcher.py
```

Or if you've made it executable:

```bash
./tmux-theme-switcher.py
```

### Navigation Controls

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate through themes |
| `Enter` | Apply selected theme |
| `Q` | Quit without applying |
| `Esc` | Cancel theme application dialog |

### Applying a Theme

1. Use arrow keys to browse themes
2. View the live preview on the right side
3. Press `Enter` when you find a theme you like
4. Confirm the application (backups will be created automatically)
5. The theme is applied immediately to tmux and your shell config

## 🎨 Available Themes (25+)

### 🟢 Green Themes
- **Matrix Green** - Classic bright terminal green
- **Forest Green** - Earthy, muted tones
- **Emerald** - Rich, vibrant green
- **Gruvbox Dark** - Retro groove warm colors
- **Dracula Green** - Purple background with green accents
- **Nord Aurora** - Subtle green on dark background

### 🔵 Blue Themes
- **Gemini** - Blue and gray tones
- **Tokyo Night** - Downtown Tokyo lights at night
- **Tokyo Night Storm** - Tokyo Night with lighter background
- **Solarized Dark** - Precision colors by Ethan Schoonover

### 🟣 Purple Themes
- **Purple Dream** - Vibrant purple and magenta
- **Catppuccin Mocha** - Soothing pastel theme (Mocha variant)
- **Kanagawa Wave** - Inspired by Hokusai's Great Wave

### 🌸 Pink/Rose Themes
- **Rose Pine** - All natural pine, faux fur and soho vibes
- **Rose Pine Moon** - Rose Pine with moon-inspired palette

### 🟠 Orange/Warm Themes
- **Monokai Pro** - Modern take on classic Monokai
- **Gruvbox Light** - Retro groove warm colors (light mode)

### 🟦 Cyan/Teal Themes
- **Mint/Teal** - Modern, lighter cyan-green

### ⚪ Neutral/Light Themes
- **Solarized Light** - Precision colors (light mode)
- **Catppuccin Latte** - Soothing pastel theme (Latte variant, light)

## 🖥️ Interface Layout

```
┌────────────────────────────────────────────────────────────┐
│              🎨 TMUX THEME SWITCHER                        │
│        ↑↓: Navigate | Enter: Apply | Q: Quit               │
├───────────────────┬────────────────────────────────────────┤
│ Theme List        │ Preview Panel                          │
│                   │                                        │
│ 🟢 Green          │ 📦 Selected Theme Name                 │
│   Matrix Green    │ Description of the theme               │
│ ▶ Forest Green    │                                        │
│   Emerald         │ 🎨 Color Palette:                      │
│   ...             │   ■ BG          #1a1c19                │
│                   │   ■ FG          #a9c496                │
│ 🔵 Blue           │   ■ Accent      #588157                │
│   Gemini          │   ■ Border      #739372                │
│   Tokyo Night     │                                        │
│   ...             │ 📊 Tmux Status Bar Preview:            │
│                   │ ┌──────────────────────────────────┐   │
│                   │ │[Session] 1:bash* 2:vim    14:23 │   │
│                   │ └──────────────────────────────────┘   │
│                   │                                        │
│                   │ 💻 Code Sample:                        │
│                   │   def hello_world():                   │
│                   │       print('Hello, World!')           │
│                   │       return True                      │
├───────────────────┴────────────────────────────────────────┤
│ Press ENTER to apply this theme (backups will be created) │
└────────────────────────────────────────────────────────────┘
```

## 🔧 What Gets Modified

When you apply a theme, the following files are modified (with automatic backups):

### 1. `~/.tmux.conf`
- Status bar colors
- Pane border colors
- Window status colors
- Message area colors
- Activity monitoring colors

**Backup location:** `~/.tmux.conf.backup.YYYYMMDD_HHMMSS`

### 2. `~/.zshrc` or `~/.bashrc`
- `EZA_COLORS` environment variable (directory colors)
- `LS_COLORS` environment variable (fallback)
- `BAT_THEME` (syntax highlighting)
- `FZF_DEFAULT_OPTS` (fuzzy finder colors)
- `PS1` prompt configuration
- Aliases for `ll` and `llt`

**Backup location:** `~/.zshrc.backup.YYYYMMDD_HHMMSS` or `~/.bashrc.backup.YYYYMMDD_HHMMSS`

## 📦 Backup System

Every time you apply a theme:

1. **Automatic Backups Created** - Timestamped backups are created in your home directory
2. **Backup Format:** `<original-file>.backup.YYYYMMDD_HHMMSS`
3. **Example:** `~/.tmux.conf.backup.20250111_143022`

### Restoring from Backup

To restore a previous configuration:

```bash
# List backups
ls -la ~/ | grep backup

# Restore tmux config
cp ~/.tmux.conf.backup.20250111_143022 ~/.tmux.conf

# Restore shell config
cp ~/.zshrc.backup.20250111_143022 ~/.zshrc

# Reload tmux
tmux source-file ~/.tmux.conf

# Reload shell
source ~/.zshrc
```

## 🎯 Advantages Over Bash Version

| Feature | Bash Script | Python TUI |
|---------|-------------|------------|
| Interface | Text menu | Interactive split-screen TUI |
| Navigation | Type number | Arrow keys |
| Preview | None | Live preview with colors, tmux bar, code |
| Themes | 8 themes | 25+ themes |
| Organization | Linear list | Categorized by color |
| Visual Feedback | Basic | Rich visual feedback |
| Theme Info | Basic description | Detailed swatches + preview |
| User Experience | Functional | Delightful |

## 🐛 Troubleshooting

### Theme not applying to tmux

```bash
# Manually reload tmux config
tmux source-file ~/.tmux.conf
```

### Colors not showing correctly

- Ensure your terminal supports 256 colors
- Try a different terminal (iTerm2, Alacritty, or modern GNOME Terminal recommended)

### Curses errors on Windows

- The script is designed for Linux/macOS
- On Windows, use WSL (Windows Subsystem for Linux)

### Interface looks broken

- Ensure your terminal window is at least 80x24 characters
- Try maximizing your terminal window

## 🔍 Theme Details

Each theme includes:

- **Background color** - Main background
- **Foreground color** - Main text color
- **Accent color** - Highlights and active elements
- **Border colors** - Pane borders (active and inactive)
- **Message colors** - Command/message area
- **Activity color** - Window activity indicators
- **Directory color** - File listing colors (for `ls`/`eza`)
- **Bat theme** - Syntax highlighting theme
- **PS1 color** - Shell prompt color

## 🎨 Adding Custom Themes

To add your own theme, edit the `THEMES` dictionary in the script:

```python
Theme(
    name="My Custom Theme",
    category="custom",
    description="My awesome theme",
    bg_color="#000000",
    fg_color="#ffffff",
    accent_color="#ff0000",
    border_color="#333333",
    border_active="#ff0000",
    inactive_bg="#111111",
    message_bg="#ff0000",
    message_fg="#000000",
    activity_color="#ff0000",
    dir_color="01;31",  # ANSI color code
    bat_theme="Monokai Extended",
    ps1_color="\\[\\033[01;31m\\]",
    color_swatches={
        "BG": "#000000",
        "FG": "#ffffff",
        "Red": "#ff0000",
    }
)
```

Add it to the appropriate category in the `THEMES` dictionary.

## 📚 Related Files

- **Original Bash Script:** `/home/user/environmentConfigurator/scripts/tmux-theme-switcher.sh`
- **Python Version:** `/home/user/environmentConfigurator/scripts/tmux-theme-switcher.py`
- **Tmux Config:** `~/.tmux.conf`
- **Shell Config:** `~/.zshrc` or `~/.bashrc`

## 🤝 Contributing

Found a bug or want to add a theme? Feel free to:

1. Report issues
2. Submit pull requests
3. Suggest new themes

## 📄 License

This project is part of the environmentConfigurator repository.

## 🙏 Credits

This theme switcher includes color palettes from many popular themes:

- **Catppuccin** - @catppuccin
- **Tokyo Night** - @folke
- **Gruvbox** - @morhetz
- **Solarized** - Ethan Schoonover
- **Monokai Pro** - monokai.pro
- **Rose Pine** - @rose-pine
- **Kanagawa** - @rebelot
- **Dracula** - @dracula
- **Nord** - @arcticicestudio

## 🎉 Enjoy!

Happy theming! May your terminal be forever beautiful! 🌈

---

**Last Updated:** 2025-01-11
**Version:** 1.0.0
**Python Version:** 3.6+
