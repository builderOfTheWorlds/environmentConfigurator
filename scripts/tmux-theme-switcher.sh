#!/bin/bash

# Tmux Theme Switcher
# Select and apply green color schemes to tmux

TMUX_CONF="$HOME/.tmux.conf"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  TMUX GREEN THEME SWITCHER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Available color schemes:"
echo ""
echo "  1. Matrix Green - Classic bright terminal green"
echo "  2. Forest Green - Earthy, muted tones"
echo "  3. Mint/Teal - Modern, lighter cyan-green"
echo "  4. Emerald - Rich, vibrant green"
echo "  5. Nord Aurora - Subtle green on dark background"
echo "  6. Dracula Green - Purple background with green"
echo ""
read -p "Select a theme (1-6): " choice

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

echo ""
echo "✓ Theme '$THEME_NAME' applied successfully!"
echo "✓ Backup saved to: $TMUX_CONF.backup"
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
