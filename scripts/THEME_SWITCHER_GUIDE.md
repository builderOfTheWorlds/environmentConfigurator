# Tmux Theme Switcher - Enhanced Guide

## Overview
The tmux-theme-switcher now includes support for:
- **Color schemes** for tmux interface
- **Directory colors** for `ls`/`eza` commands
- **Font configuration** for terminal emulators

## Usage

Run the script:
```bash
./tmux-theme-switcher.sh
```

You'll be prompted to:
1. Select a color theme (1-6)
2. See which fonts are available on your system
3. Select a font (0 to keep current, or choose from available fonts)

**Example Font Menu:**
```
Available fonts:

  0. Keep current font
     Current: Ubuntu Mono 13

  1. Ubuntu Mono
  2. DejaVu Sans Mono <--- current
  3. Hack

Select font (0-3, default: 0):
```

## Available Themes

### 1. Matrix Green
- **Style**: Classic bright terminal green on black
- **Directory Color**: Bright green
- **Best for**: Retro terminal aesthetics

### 2. Forest Green
- **Style**: Earthy, muted olive and sage tones
- **Directory Color**: Muted olive green
- **Best for**: Easy on the eyes, natural look

### 3. Mint/Teal
- **Style**: Modern cyan-green aesthetic
- **Directory Color**: Bright cyan
- **Best for**: Contemporary, clean interface

### 4. Emerald
- **Style**: Rich vibrant green
- **Directory Color**: Bright emerald
- **Best for**: Bold, eye-catching display

### 5. Nord Aurora
- **Style**: Subtle Nord-inspired palette
- **Directory Color**: Nord frost green
- **Best for**: Professional, minimalist setup

### 6. Dracula Green
- **Style**: Popular Dracula theme variant
- **Directory Color**: Dracula green
- **Best for**: Dark theme enthusiasts

## Font Options

The script now **dynamically detects** which fonts are installed on your system and only shows available ones!

**Supported Fonts** (if installed):
- **JetBrains Mono** - Modern, clear (11pt)
- **Fira Code** - Popular with ligatures (11pt)
- **Hack** - Clean, readable (11pt)
- **Source Code Pro** - Adobe's coding font (11pt)
- **Ubuntu Mono** - Ubuntu's default (13pt)
- **DejaVu Sans Mono** - Fallback monospace (11pt)
- **Noto Mono** - Google's monospace (11pt)
- **Liberation Mono** - Open source alternative (11pt)

**Features:**
- Only shows fonts installed on your system
- Detects and marks your current font with `<--- current`
- Option 0 to keep current font unchanged

## What Gets Changed

### Tmux Configuration (`~/.tmux.conf`)
- Status bar colors
- Pane border colors
- Window status indicators
- Message/command area colors
- Activity monitoring colors

### Shell Configuration (`~/.zshrc`)
- `EZA_COLORS` environment variable
- `LS_COLORS` environment variable (fallback)
- Font information comment

### Terminal Font (if changed)
- **GNOME Terminal**: Via gsettings
- **Alacritty**: Via config file (~/.config/alacritty/)

## Applying Changes

After running the script:

1. **For tmux changes**: Automatically reloaded if tmux is running
2. **For shell colors**: Run `source ~/.zshrc` or restart terminal
3. **For fonts**: Restart terminal application

## Directory Color Codes

The script configures these directory colors per theme:
- **Matrix Green**: `01;32` (Bright green)
- **Forest Green**: `01;38;5;108` (Muted olive)
- **Mint/Teal**: `01;36` (Bright cyan)
- **Emerald**: `01;38;5;79` (Bright emerald)
- **Nord Aurora**: `01;38;5;150` (Nord frost)
- **Dracula Green**: `01;38;5;84` (Dracula green)

## Color Code Format

ANSI color codes format: `attribute;foreground;background`
- `01` = Bold
- `38;5;N` = 256-color foreground (N = color number)
- Standard colors: 30-37 (foreground), 40-47 (background)

## Troubleshooting

### Colors not showing
```bash
# Reload shell config
source ~/.zshrc

# Or restart terminal
```

### Font not changing
- Ensure the font is installed on your system
- Install fonts via: `sudo apt install fonts-jetbrains-mono fonts-firacode fonts-hack`
- Restart terminal application after font changes

### Tmux not updating
```bash
# Manually reload tmux config
tmux source-file ~/.tmux.conf
```

## Customization

To customize directory colors manually, edit the `DIR_COLOR` variable in each theme section of `/home/matt/tmux-theme-switcher.sh`.

Example:
```bash
DIR_COLOR="01;35"  # Bright magenta instead of green
```

## File Locations

- **Script**: `/home/matt/tmux-theme-switcher.sh`
- **Tmux config**: `~/.tmux.conf`
- **Shell config**: `~/.zshrc`
- **Backup**: `~/.tmux.conf.backup` (auto-created)

## Quick Test

After running the switcher:
```bash
source ~/.zshrc
ll
```

Directories should now appear in your selected theme color instead of yellow!
