# Tmux Theme Switcher

A comprehensive theme management tool for tmux that also configures shell colors and terminal fonts.

## Features

- **6 Green-themed Color Schemes** for tmux
- **Directory Color Customization** (changes the yellow directories in `ll`)
- **Bash/Shell Color Integration**:
  - Bat syntax highlighting themes
  - FZF fuzzy finder colors
  - Coordinated color scheme across all tools
- **Dynamic Font Detection** (only shows installed fonts)
- **Current Settings Detection** (shows what you're currently using with `<--- current`)
- **Automatic Configuration** of tmux, shell, and terminal

## Quick Start

```bash
cd ~/tmux-theme-switcher
./tmux-theme-switcher.sh
```

Follow the prompts to:
1. Select your color theme
2. Select your font (or keep current)

Then apply changes:
```bash
source ~/.zshrc
```

## Directory Structure

```
tmux-theme-switcher/
├── README.md                    # This file
├── THEME_SWITCHER_GUIDE.md     # Detailed guide
└── tmux-theme-switcher.sh      # Main script
```

## Available Themes

| # | Theme Name     | Style                              | Directory Color    | Bat Theme              |
|---|----------------|------------------------------------|--------------------|------------------------|
| 1 | Matrix Green   | Classic bright terminal green      | Bright green       | DarkNeon               |
| 2 | Forest Green   | Earthy, muted tones                | Muted olive green  | Nord                   |
| 3 | Mint/Teal      | Modern, lighter cyan-green         | Bright cyan        | Monokai Extended       |
| 4 | Emerald        | Rich, vibrant green                | Bright emerald     | Monokai Extended Bright|
| 5 | Nord Aurora    | Subtle green on dark background    | Nord frost green   | Nord                   |
| 6 | Dracula Green  | Purple background with green       | Dracula green      | Dracula                |
| 7 | Purple Dream   | Vibrant purple and magenta         | Bright magenta     | Dracula                |

## What Gets Changed

### When You Run the Script:

1. **Tmux Configuration** (`~/.tmux.conf`)
   - Status bar colors
   - Pane borders
   - Window indicators
   - Message areas

2. **Shell Configuration** (`~/.zshrc`)
   - `EZA_COLORS` - Directory colors for `eza`/`ll` command
   - `LS_COLORS` - Fallback for standard `ls`
   - `BAT_THEME` - Syntax highlighting theme for `bat`
   - `FZF_DEFAULT_OPTS` - Fuzzy finder colors
   - Theme name marker (for detection)

3. **Terminal Font** (optional)
   - GNOME Terminal settings
   - Alacritty config files

### Backups

- Tmux config backed up to: `~/.tmux.conf.backup`

## Example Output

### Theme Selection
```
Available color schemes:

  1. Matrix Green - Classic bright terminal green
  2. Forest Green - Earthy, muted tones
  3. Mint/Teal - Modern, lighter cyan-green <--- current
  4. Emerald - Rich, vibrant green
  5. Nord Aurora - Subtle green on dark background
  6. Dracula Green - Purple background with green

Select a theme (1-6):
```

### Font Selection
```
Checking available fonts...

Available fonts:

  0. Keep current font
     Current: Ubuntu Mono 13

  1. Ubuntu Mono <--- current
  2. DejaVu Sans Mono
  3. Hack

Select font (0-3, default: 0):
```

## Supported Fonts

The script checks for these fonts and only shows installed ones:
- JetBrains Mono (11pt)
- Fira Code (11pt)
- Hack (11pt)
- Source Code Pro (11pt)
- Ubuntu Mono (13pt)
- DejaVu Sans Mono (11pt)
- Noto Mono (11pt)
- Liberation Mono (11pt)

## Installation

### Install Additional Fonts (Optional)

```bash
# Install popular coding fonts
sudo apt install fonts-jetbrains-mono fonts-firacode fonts-hack

# Or on Fedora/RHEL
sudo dnf install jetbrains-mono-fonts fira-code-fonts
```

## Usage Tips

### After Changing Theme
```bash
# Apply shell color changes immediately
source ~/.zshrc

# Test directory colors
ll

# Test bat syntax highlighting
cat ~/.zshrc

# Test fzf colors (Ctrl+R for history search)
```

### If Tmux Isn't Running
The script will still configure everything. Start tmux to see changes:
```bash
tmux
```

### Manual Reload
```bash
# Reload tmux config manually
tmux source-file ~/.tmux.conf

# Reload shell config
source ~/.zshrc
```

## Troubleshooting

### Colors Not Showing
```bash
# Reload shell configuration
source ~/.zshrc

# Or restart your terminal
```

### Font Not Changing
- Ensure the font is installed: `fc-list | grep "FontName"`
- Install missing fonts (see Installation section)
- Restart your terminal application

### Theme Not Detected
- The script marks the current theme in `~/.zshrc`
- If you manually edited configs, detection may fail
- Just select your desired theme - it will update correctly

## Customization

### Adding Custom Themes

Edit `tmux-theme-switcher.sh` and add to the theme case statement:

```bash
7)
    echo "Applying My Custom Theme..."
    THEME_NAME="My Custom Theme"
    BG_COLOR="#RRGGBB"
    FG_COLOR="#RRGGBB"
    # ... other color definitions
    DIR_COLOR="01;32"  # ANSI color code
    ;;
```

### Custom Directory Colors

Directory color format: `attribute;color`
- `01` = Bold
- `32` = Green
- `36` = Cyan
- `38;5;N` = 256-color (N = 0-255)

Examples:
```bash
DIR_COLOR="01;35"      # Bright magenta
DIR_COLOR="38;5;208"   # Orange (256-color)
DIR_COLOR="01;38;5;79" # Bright emerald
```

## Files Modified

| File | Purpose | Backed Up? |
|------|---------|------------|
| `~/.tmux.conf` | Tmux colors and settings | Yes (`.backup`) |
| `~/.zshrc` | Shell colors and theme marker | No |
| `~/.config/alacritty/*` | Font settings (if exists) | No |

## Documentation

- **README.md** (this file) - Quick reference
- **THEME_SWITCHER_GUIDE.md** - Detailed guide with color codes and advanced usage

## Requirements

- Bash
- Tmux (for tmux theming)
- Zsh (for shell color configuration)
- `fc-list` (for font detection, usually part of fontconfig)
- Optional: GNOME Terminal or Alacritty for font changes

## License

Free to use and modify.

## Contributing

Feel free to add more themes, fonts, or terminal emulator support!
