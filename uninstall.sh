#!/bin/bash

#
# Environment Configurator - Uninstall Script
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

INSTALL_DIR="$HOME/.environment-config"

echo -e "${YELLOW}Environment Configurator - Uninstall${NC}"
echo "=============================================="
echo ""

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# Remove symlinks
print_status "Removing dotfile symlinks..."
for file in "$INSTALL_DIR"/dotfiles/.*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        if [ "$filename" != "." ] && [ "$filename" != ".." ]; then
            rm -f "$HOME/$filename"
        fi
    fi
done

for file in "$INSTALL_DIR"/dotfiles/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        rm -f "$HOME/.$filename"
    fi
done

# Remove scripts
print_status "Removing scripts..."
for script in "$INSTALL_DIR"/scripts/*; do
    if [ -f "$script" ]; then
        scriptname=$(basename "$script")
        rm -f "$HOME/bin/$scriptname"
    fi
done
rm -f "$HOME/bin/update-env-config"

# Remove cron job
print_status "Removing auto-update cron job..."
crontab -l 2>/dev/null | grep -v "$INSTALL_DIR" | crontab - || true

# Remove repository
print_status "Removing installation directory..."
rm -rf "$INSTALL_DIR"

echo ""
echo -e "${GREEN}Uninstall complete!${NC}"
echo ""
echo "Note: Your backup files are still preserved."
echo "Check ~/.environment-config-backup-* directories"
