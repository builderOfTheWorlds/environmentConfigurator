#!/bin/bash

#
# Environment Configurator - Installation Script
# Usage: curl -fsSL https://raw.githubusercontent.com/YOURUSERNAME/YOURREPO/main/install.sh | bash
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/YOURUSERNAME/YOURREPO.git"
INSTALL_DIR="$HOME/.environment-config"
BACKUP_DIR="$HOME/.environment-config-backup-$(date +%Y%m%d-%H%M%S)"

echo -e "${GREEN}Environment Configurator - Installation${NC}"
echo "=============================================="
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Backup existing files
backup_file() {
    local file=$1
    if [ -f "$HOME/$file" ]; then
        mkdir -p "$BACKUP_DIR"
        cp "$HOME/$file" "$BACKUP_DIR/"
        print_warning "Backed up existing $file to $BACKUP_DIR"
    fi
}

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    print_status "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    print_status "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Backup existing dotfiles
print_status "Backing up existing configuration files..."
backup_file ".bashrc"
backup_file ".zshrc"
backup_file ".gitconfig"
backup_file ".tmux.conf"

# Create symlinks for dotfiles
print_status "Installing dotfiles..."
for file in "$INSTALL_DIR"/dotfiles/.*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        # Skip . and ..
        if [ "$filename" != "." ] && [ "$filename" != ".." ]; then
            ln -sf "$file" "$HOME/$filename"
            print_status "Linked $filename"
        fi
    fi
done

# Also handle non-hidden files in dotfiles directory
for file in "$INSTALL_DIR"/dotfiles/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        # Add dot prefix for home directory
        ln -sf "$file" "$HOME/.$filename"
        print_status "Linked .$filename"
    fi
done

# Install scripts to ~/bin
print_status "Installing scripts..."
mkdir -p "$HOME/bin"
for script in "$INSTALL_DIR"/scripts/*; do
    if [ -f "$script" ]; then
        scriptname=$(basename "$script")
        ln -sf "$script" "$HOME/bin/$scriptname"
        chmod +x "$HOME/bin/$scriptname"
        print_status "Installed $scriptname"
    fi
done

# Add ~/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    if [ -f "$HOME/.bashrc" ]; then
        echo '' >> "$HOME/.bashrc"
        echo '# Add ~/bin to PATH' >> "$HOME/.bashrc"
        echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bashrc"
        print_status "Added ~/bin to PATH in .bashrc"
    fi
    if [ -f "$HOME/.zshrc" ]; then
        echo '' >> "$HOME/.zshrc"
        echo '# Add ~/bin to PATH' >> "$HOME/.zshrc"
        echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
        print_status "Added ~/bin to PATH in .zshrc"
    fi
fi

# Setup auto-update via cron (optional)
print_status "Setting up auto-update..."
CRON_CMD="0 */6 * * * cd $INSTALL_DIR && git pull origin main > /dev/null 2>&1"
(crontab -l 2>/dev/null | grep -v "$INSTALL_DIR" ; echo "$CRON_CMD") | crontab -
print_status "Auto-update scheduled (every 6 hours)"

# Create update script
cat > "$HOME/bin/update-env-config" << 'UPDATESCRIPT'
#!/bin/bash
cd "$HOME/.environment-config" && git pull origin main
echo "Environment configuration updated!"
UPDATESCRIPT
chmod +x "$HOME/bin/update-env-config"
print_status "Created update-env-config command"

echo ""
echo -e "${GREEN}=============================================="
echo "Installation complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
echo "2. Run 'update-env-config' anytime to pull latest changes"
echo ""
if [ -d "$BACKUP_DIR" ]; then
    echo "Your old configuration files are backed up in:"
    echo "$BACKUP_DIR"
    echo ""
fi
