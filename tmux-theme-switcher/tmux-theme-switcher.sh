#!/bin/bash

# Tmux Theme Switcher
# Select and apply green color schemes to tmux

TMUX_CONF="$HOME/.tmux.conf"

# Detect user's shell
USER_SHELL=$(basename "$SHELL")
if [ "$USER_SHELL" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
else
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TMUX GREEN THEME SWITCHER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ========================================
# Detect Current Theme
# ========================================

CURRENT_THEME_NAME="Unknown"

# Try to detect from shell rc file
if [ -f "$SHELL_RC" ] && grep -q "# Theme:" "$SHELL_RC"; then
    CURRENT_THEME_NAME=$(grep "# Theme:" "$SHELL_RC" | head -1 | sed 's/# Theme: *//')
fi

# Define available themes
declare -a THEME_NAMES=(
    "Matrix Green"
    "Forest Green"
    "Mint/Teal"
    "Emerald"
    "Nord Aurora"
    "Dracula Green"
    "Purple Dream"
)

declare -a THEME_DESCRIPTIONS=(
    "Classic bright terminal green"
    "Earthy, muted tones"
    "Modern, lighter cyan-green"
    "Rich, vibrant green"
    "Subtle green on dark background"
    "Purple background with green"
    "Vibrant purple and magenta"
)

# Display theme menu
echo "Available color schemes:"
echo ""

for i in "${!THEME_NAMES[@]}"; do
    theme_num=$((i + 1))
    marker=""
    if [ "${THEME_NAMES[$i]}" = "$CURRENT_THEME_NAME" ]; then
        marker=" <--- current"
    fi
    echo "  $theme_num. ${THEME_NAMES[$i]} - ${THEME_DESCRIPTIONS[$i]}$marker"
done

echo ""
read -p "Select a theme (1-${#THEME_NAMES[@]}): " choice
echo ""

# ========================================
# Detect Current Font
# ========================================

CURRENT_FONT="Unknown"

# Try to detect from GNOME Terminal
if command -v gsettings &> /dev/null && gsettings list-schemas | grep -q "org.gnome.Terminal" 2>/dev/null; then
    PROFILE=$(gsettings get org.gnome.Terminal.ProfilesList default 2>/dev/null | tr -d "'")
    if [ -n "$PROFILE" ]; then
        CURRENT_FONT=$(gsettings get org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/ font 2>/dev/null | tr -d "'")
    fi
fi

# Try to detect from Alacritty
if [ "$CURRENT_FONT" = "Unknown" ]; then
    ALACRITTY_CONF="$HOME/.config/alacritty/alacritty.yml"
    ALACRITTY_CONF_TOML="$HOME/.config/alacritty/alacritty.toml"

    if [ -f "$ALACRITTY_CONF" ]; then
        CURRENT_FONT=$(grep "family:" "$ALACRITTY_CONF" | head -1 | sed 's/.*family: *//' | tr -d '"' | tr -d "'")
    elif [ -f "$ALACRITTY_CONF_TOML" ]; then
        CURRENT_FONT=$(grep "family =" "$ALACRITTY_CONF_TOML" | head -1 | sed 's/.*family = *//' | tr -d '"' | tr -d "'")
    fi
fi

# Try to detect from shell rc marker (fallback)
if [ "$CURRENT_FONT" = "Unknown" ] && [ -f "$SHELL_RC" ] && grep -q "# TERMINAL FONT:" "$SHELL_RC"; then
    CURRENT_FONT=$(grep "# TERMINAL FONT:" "$SHELL_RC" | head -1 | sed 's/# TERMINAL FONT: *//' | sed 's/ ([0-9]* pt)//')
fi

# ========================================
# Check Available Fonts and Build Menu
# ========================================

echo "Checking available fonts..."
echo ""

# Define fonts to check
declare -a FONT_LIST=(
    "JetBrains Mono"
    "Fira Code"
    "Hack"
    "Source Code Pro"
    "Ubuntu Mono"
    "DejaVu Sans Mono"
    "Noto Mono"
    "Liberation Mono"
)

# Check which fonts are installed
declare -a AVAILABLE_FONTS=()
declare -a AVAILABLE_INDICES=()
font_index=1

for font in "${FONT_LIST[@]}"; do
    if fc-list | grep -qi "$font"; then
        AVAILABLE_FONTS+=("$font")
        AVAILABLE_INDICES+=($font_index)
        font_index=$((font_index + 1))
    fi
done

# Display available fonts
echo "Available fonts:"
echo ""
echo "  0. Keep current font"
if [ "$CURRENT_FONT" != "Unknown" ]; then
    echo "     Current: $CURRENT_FONT"
fi
echo ""

menu_index=1
for font in "${AVAILABLE_FONTS[@]}"; do
    # Check if this is the current font
    marker=""
    if echo "$CURRENT_FONT" | grep -qi "$font"; then
        marker=" <--- current"
    fi
    echo "  $menu_index. $font$marker"
    menu_index=$((menu_index + 1))
done

echo ""
read -p "Select font (0-$((${#AVAILABLE_FONTS[@]})), default: 0): " font_choice
font_choice=${font_choice:-0}

case $choice in
    1)
        echo "Applying Matrix Green..."
        THEME_NAME="Matrix Green"
        BG_COLOR="#000000"
        FG_COLOR="#ccffcc"
        ACCENT_COLOR="#00ff00"
        BORDER_COLOR="#00aa00"
        BORDER_ACTIVE="#00ff00"
        INACTIVE_BG="#1a1a1a"
        MESSAGE_BG="#00ff00"
        MESSAGE_FG="#000000"
        ACTIVITY_COLOR="#00ff00"
        # Directory colors for ls/eza
        DIR_COLOR="01;32"  # Bright green
        # Bash/Terminal colors
        BAT_THEME="DarkNeon"
        PS1_COLOR="\\[\\033[01;32m\\]"  # Bright green prompt
        PS1_RESET="\\[\\033[00m\\]"
        ;;
    2)
        echo "Applying Forest Green..."
        THEME_NAME="Forest Green"
        BG_COLOR="#1a1c19"
        FG_COLOR="#a9c496"
        ACCENT_COLOR="#588157"
        BORDER_COLOR="#2d3325"
        BORDER_ACTIVE="#739372"
        INACTIVE_BG="#232620"
        MESSAGE_BG="#588157"
        MESSAGE_FG="#1a1c19"
        ACTIVITY_COLOR="#88aa77"
        # Directory colors for ls/eza
        DIR_COLOR="01;38;5;108"  # Muted olive green
        # Bash/Terminal colors
        BAT_THEME="Nord"
        PS1_COLOR="\\[\\033[38;5;108m\\]"  # Muted olive prompt
        PS1_RESET="\\[\\033[00m\\]"
        ;;
    3)
        echo "Applying Mint/Teal..."
        THEME_NAME="Mint/Teal"
        BG_COLOR="#161b22"
        FG_COLOR="#afebdc"
        ACCENT_COLOR="#2ed5b6"
        BORDER_COLOR="#233732"
        BORDER_ACTIVE="#40c4a9"
        INACTIVE_BG="#1c2128"
        MESSAGE_BG="#2ed5b6"
        MESSAGE_FG="#161b22"
        ACTIVITY_COLOR="#58d9c0"
        # Directory colors for ls/eza
        DIR_COLOR="01;36"  # Bright cyan
        # Bash/Terminal colors
        BAT_THEME="Monokai Extended"
        PS1_COLOR="\\[\\033[01;36m\\]"  # Bright cyan prompt
        PS1_RESET="\\[\\033[00m\\]"
        ;;
    4)
        echo "Applying Emerald..."
        THEME_NAME="Emerald"
        BG_COLOR="#101816"
        FG_COLOR="#d1fae5"
        ACCENT_COLOR="#34d399"
        BORDER_COLOR="#1f2f29"
        BORDER_ACTIVE="#6ee7b7"
        INACTIVE_BG="#172320"
        MESSAGE_BG="#34d399"
        MESSAGE_FG="#101816"
        ACTIVITY_COLOR="#5de4a8"
        # Directory colors for ls/eza
        DIR_COLOR="01;38;5;79"  # Bright emerald
        # Bash/Terminal colors
        BAT_THEME="Monokai Extended Bright"
        PS1_COLOR="\\[\\033[38;5;79m\\]"  # Bright emerald prompt
        PS1_RESET="\\[\\033[00m\\]"
        ;;
    5)
        echo "Applying Nord Aurora..."
        THEME_NAME="Nord Aurora"
        BG_COLOR="#2e3440"
        FG_COLOR="#d8dee9"
        ACCENT_COLOR="#a3be8c"
        BORDER_COLOR="#3b4252"
        BORDER_ACTIVE="#88c0d0"
        INACTIVE_BG="#3b4252"
        MESSAGE_BG="#a3be8c"
        MESSAGE_FG="#2e3440"
        ACTIVITY_COLOR="#88c0d0"
        # Directory colors for ls/eza
        DIR_COLOR="01;38;5;150"  # Nord frost green
        # Bash/Terminal colors
        BAT_THEME="Nord"
        PS1_COLOR="\\[\\033[38;5;150m\\]"  # Nord frost prompt
        PS1_RESET="\\[\\033[00m\\]"
        ;;
    6)
        echo "Applying Dracula Green..."
        THEME_NAME="Dracula Green"
        BG_COLOR="#282a36"
        FG_COLOR="#f8f8f2"
        ACCENT_COLOR="#50fa7b"
        BORDER_COLOR="#44475a"
        BORDER_ACTIVE="#8be9fd"
        INACTIVE_BG="#343746"
        MESSAGE_BG="#50fa7b"
        MESSAGE_FG="#282a36"
        ACTIVITY_COLOR="#50fa7b"
        # Directory colors for ls/eza
        DIR_COLOR="01;38;5;84"  # Dracula green
        # Bash/Terminal colors
        BAT_THEME="Dracula"
        PS1_COLOR="\\[\\033[38;5;84m\\]"  # Dracula green prompt
        PS1_RESET="\\[\\033[00m\\]"
        ;;
    7)
        echo "Applying Purple Dream..."
        THEME_NAME="Purple Dream"
        BG_COLOR="#1a0d2e"
        FG_COLOR="#e0c3fc"
        ACCENT_COLOR="#b565d8"
        BORDER_COLOR="#3d2b5c"
        BORDER_ACTIVE="#d896ff"
        INACTIVE_BG="#251640"
        MESSAGE_BG="#b565d8"
        MESSAGE_FG="#1a0d2e"
        ACTIVITY_COLOR="#d896ff"
        # Directory colors for ls/eza
        DIR_COLOR="01;35"  # Bright magenta/purple
        # Bash/Terminal colors
        BAT_THEME="Dracula"
        PS1_COLOR="\\[\\033[01;35m\\]"  # Bright purple prompt
        PS1_RESET="\\[\\033[00m\\]"
        ;;
    *)
        echo "Invalid selection. Exiting."
        exit 1
        ;;
esac

# Backup current config
cp "$TMUX_CONF" "$TMUX_CONF.backup"

# Find the theme section and replace it
sed -i '/^# ========================================$/,/^# ========================================$/ {
    /^# Theme/,/^# ========================================$/ {
        /^# Theme/ {
            a\
# ========================================\

            a\
\

            a\
# Status bar colors\

            a\
set -g status-style bg='"$BG_COLOR"',fg='"$FG_COLOR"'\

            a\
set -g status-left-style bg='"$BG_COLOR"',fg='"$ACCENT_COLOR"'\

            a\
set -g status-right-style bg='"$BG_COLOR"',fg='"$FG_COLOR"'\

            a\
\

            a\
# Pane border colors\

            a\
set -g pane-border-style fg='"$BORDER_COLOR"'\

            a\
set -g pane-active-border-style fg='"$BORDER_ACTIVE"'\

            a\
\

            a\
# Window status colors\

            a\
setw -g window-status-style fg='"$FG_COLOR"',bg='"$BG_COLOR"'\

            a\
setw -g window-status-current-style fg='"$BG_COLOR"',bg='"$ACCENT_COLOR"',bold\

            a\
\

            a\
# Message colors\

            a\
set -g message-style bg='"$MESSAGE_BG"',fg='"$MESSAGE_FG"',bold\

            a\
set -g message-command-style bg='"$MESSAGE_BG"',fg='"$MESSAGE_FG"',bold
            d
        }
        d
    }
}' "$TMUX_CONF"

# Also update the status-left to use the accent color
sed -i "s|set -g status-left \"#\[fg=#[^,]*,bg=$ACCENT_COLOR,bold\]|set -g status-left \"#[fg=$BG_COLOR,bg=$ACCENT_COLOR,bold]|" "$TMUX_CONF"
sed -i "s|set -g status-left \"#\[fg=#[^,]*,bg=#[^,]*,bold\] #S #\[fg=#[^,]*,bg=#[^,]*,nobold\]|set -g status-left \"#[fg=$BG_COLOR,bg=$ACCENT_COLOR,bold] #S #[fg=$ACCENT_COLOR,bg=$BG_COLOR,nobold]\"|" "$TMUX_CONF"

# Update activity color
sed -i "s|setw -g window-status-activity-style fg=#[^,]*,bg=#[^,]*|setw -g window-status-activity-style fg=$ACTIVITY_COLOR,bg=$BG_COLOR|" "$TMUX_CONF"

# ========================================
# Configure Shell Colors (LS_COLORS/EZA_COLORS)
# ========================================

# Remove any old color exports that might conflict
sed -i '/^export LS_COLORS=/d' "$SHELL_RC"
sed -i '/^export EZA_COLORS=/d' "$SHELL_RC"

# Create or update the color configuration section in shell rc
if grep -q "# ======================================== TMUX THEME COLORS" "$SHELL_RC"; then
    # Remove existing color config section
    sed -i '/# ======================================== TMUX THEME COLORS/,/# ======================================== END TMUX THEME COLORS/d' "$SHELL_RC"
fi

# Add new color configuration
cat >> "$SHELL_RC" << EOF

# ======================================== TMUX THEME COLORS
# Auto-generated by tmux-theme-switcher
# Theme: $THEME_NAME
# ========================================

# EZA color configuration (for directory colors)
export EZA_COLORS="di=$DIR_COLOR:ln=01;36:so=01;35:pi=40;33:ex=01;31:bd=40;33;01:cd=40;33;01:su=37;41:sg=30;43:tw=30;42:ow=34;42"

# Traditional LS_COLORS (fallback for standard ls command)
export LS_COLORS="di=$DIR_COLOR:ln=01;36:so=01;35:pi=40;33:ex=01;31:bd=40;33;01:cd=40;33;01:su=37;41:sg=30;43:tw=30;42:ow=34;42"

# Bat theme (syntax highlighting)
export BAT_THEME="$BAT_THEME"

# FZF colors (matching theme)
export FZF_DEFAULT_OPTS="--color=fg:-1,bg:-1,hl:$DIR_COLOR,fg+:#ffffff,bg+:#3a3a3a,hl+:$DIR_COLOR --color=info:$DIR_COLOR,prompt:$DIR_COLOR,pointer:$DIR_COLOR,marker:$DIR_COLOR,spinner:$DIR_COLOR"

# ======================================== END TMUX THEME COLORS
EOF

# ========================================
# Configure Terminal Font
# ========================================

# Validate font choice
if ! [[ "$font_choice" =~ ^[0-9]+$ ]] || [ "$font_choice" -gt "${#AVAILABLE_FONTS[@]}" ]; then
    echo "Invalid font selection. Keeping current font."
    font_choice=0
fi

if [ "$font_choice" -eq 0 ]; then
    echo "Keeping current font configuration..."
    FONT_NAME="Current"
else
    # Get selected font from array (index is choice - 1)
    SELECTED_FONT="${AVAILABLE_FONTS[$((font_choice - 1))]}"
    FONT_NAME="$SELECTED_FONT"
    FONT_FAMILY="$SELECTED_FONT"

    # Set default size based on font
    case "$SELECTED_FONT" in
        "Ubuntu Mono")
            FONT_SIZE="13"
            ;;
        *)
            FONT_SIZE="11"
            ;;
    esac

    echo "Selected font: $FONT_NAME"
fi

# Apply font configuration for common terminals
if [ "$font_choice" -ne 0 ]; then
    # Configure for GNOME Terminal (if using)
    if command -v gsettings &> /dev/null && gsettings list-schemas | grep -q "org.gnome.Terminal"; then
        PROFILE=$(gsettings get org.gnome.Terminal.ProfilesList default | tr -d "'")
        if [ -n "$PROFILE" ]; then
            gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/ font "$FONT_FAMILY $FONT_SIZE"
            gsettings set org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/ use-system-font false
        fi
    fi

    # Configure for Alacritty (if config exists)
    ALACRITTY_CONF="$HOME/.config/alacritty/alacritty.yml"
    ALACRITTY_CONF_TOML="$HOME/.config/alacritty/alacritty.toml"

    if [ -f "$ALACRITTY_CONF" ]; then
        sed -i "s/family:.*/family: $FONT_FAMILY/" "$ALACRITTY_CONF"
        sed -i "s/size:.*/size: $FONT_SIZE/" "$ALACRITTY_CONF"
    elif [ -f "$ALACRITTY_CONF_TOML" ]; then
        sed -i "s/family = .*/family = \"$FONT_FAMILY\"/" "$ALACRITTY_CONF_TOML"
        sed -i "s/size = .*/size = $FONT_SIZE/" "$ALACRITTY_CONF_TOML"
    fi

    # Add font info to shell rc
    if grep -q "# TERMINAL FONT:" "$SHELL_RC"; then
        sed -i "s/# TERMINAL FONT:.*/# TERMINAL FONT: $FONT_NAME ($FONT_SIZE pt)/" "$SHELL_RC"
    else
        sed -i "/# ======================================== TMUX THEME COLORS/a # TERMINAL FONT: $FONT_NAME ($FONT_SIZE pt)" "$SHELL_RC"
    fi
fi

echo ""
echo "✓ Theme '$THEME_NAME' applied successfully!"
echo "✓ Backup saved to: $TMUX_CONF.backup"
echo ""
echo "Configured:"
echo "  • Tmux colors and borders"
echo "  • Directory colors (eza/ls): $DIR_COLOR"
echo "  • Bat syntax theme: $BAT_THEME"
echo "  • FZF fuzzy finder colors"
if [ "$font_choice" -ne 0 ]; then
    echo "  • Terminal font: $FONT_NAME ($FONT_SIZE pt)"
fi
echo ""

# Reload tmux config if tmux is running
if tmux info &> /dev/null; then
    tmux source-file "$TMUX_CONF"
    tmux display-message "Theme '$THEME_NAME' loaded!"
    echo "✓ Tmux config reloaded!"
else
    echo "Note: Tmux is not running. Start tmux to see the new theme."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  All done! Theme applied."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To see the changes, run:"
echo ""
echo "  source $SHELL_RC && ll"
echo ""
echo "This will reload your shell and show the new directory colors."
echo ""
