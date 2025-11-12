#!/bin/bash

#
# Environment Configurator - Installation Script
# Usage:
#   Normal install: curl -fsSL https://raw.githubusercontent.com/YOURUSERNAME/YOURREPO/main/install.sh | bash
#   Test mode (dry run): bash install.sh --test
#   or: curl -fsSL https://raw.githubusercontent.com/YOURUSERNAME/YOURREPO/main/install.sh | bash -s -- --test
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
TEST_MODE=false
USE_PASSWORD=false
for arg in "$@"; do
    case $arg in
        --test)
            TEST_MODE=true
            ;;
        --use-password)
            USE_PASSWORD=true
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --test           Run in test mode (dry run, no changes)"
            echo "  --use-password   Use username/password auth instead of token (legacy)"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                      # Normal install with token auth"
            echo "  $0 --test               # Test mode"
            echo "  $0 --use-password       # Use username/password auth"
            exit 0
            ;;
    esac
done

# Configuration
REPO_BASE_URL="https://github.com/builderOfTheWorlds/environmentConfigurator.git"
INSTALL_DIR="$HOME/.environment-config"
BACKUP_DIR="$HOME/.environment-config-backup-$(date +%Y%m%d-%H%M%S)"

if [ "$TEST_MODE" = true ]; then
    echo -e "${BLUE}Environment Configurator - TEST MODE${NC}"
    echo "=============================================="
    echo -e "${YELLOW}Running in test mode - no changes will be made${NC}"
else
    echo -e "${GREEN}Environment Configurator - Installation${NC}"
    echo "=============================================="
fi
echo ""

# Function to print status messages
print_status() {
    if [ "$TEST_MODE" = true ]; then
        echo -e "${BLUE}[TEST]${NC} Would: $1"
    else
        echo -e "${GREEN}[✓]${NC} $1"
    fi
}

print_warning() {
    if [ "$TEST_MODE" = true ]; then
        echo -e "${BLUE}[TEST]${NC} Would warn: $1"
    else
        echo -e "${YELLOW}[!]${NC} $1"
    fi
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Get git credentials and build authenticated URL
get_repo_url() {
    local base_url="$REPO_BASE_URL"

    # Extract components from URL
    # Expected format: https://github.com/USERNAME/REPO.git
    local url_without_protocol="${base_url#https://}"
    local host_and_path="$url_without_protocol"

    if [ "$TEST_MODE" = true ]; then
        REPO_URL="$base_url"
        return 0
    fi

    # Check if repo is public by attempting anonymous clone test
    # If it's public, no auth needed
    if git ls-remote "$base_url" HEAD &>/dev/null; then
        print_status "Repository is public, no authentication needed"
        REPO_URL="$base_url"
        return 0
    fi

    # Private repo - need credentials
    echo ""
    echo -e "${YELLOW}Authentication required for private repository${NC}"
    echo ""

    if [ "$USE_PASSWORD" = true ]; then
        # Legacy username/password authentication
        echo -e "${YELLOW}Note: Username/password auth is deprecated on GitHub.${NC}"
        echo -e "${YELLOW}Consider using a Personal Access Token instead.${NC}"
        echo ""
        read -p "GitHub Username: " gh_username
        read -sp "GitHub Password: " gh_password
        echo ""

        REPO_URL="https://${gh_username}:${gh_password}@${host_and_path}"
    else
        # Token authentication (default)
        echo "To create a Personal Access Token:"
        echo "1. Go to: https://github.com/settings/tokens"
        echo "2. Click 'Generate new token (classic)'"
        echo "3. Select scope: 'repo' (full control)"
        echo "4. Copy the generated token"
        echo ""
        read -sp "GitHub Personal Access Token: " gh_token
        echo ""

        if [ -z "$gh_token" ]; then
            print_error "Token cannot be empty"
            exit 1
        fi

        REPO_URL="https://${gh_token}@${host_and_path}"
    fi
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Get authenticated repository URL
get_repo_url

# Backup existing files
backup_file() {
    local file=$1
    if [ -f "$HOME/$file" ]; then
        if [ "$TEST_MODE" = false ]; then
            mkdir -p "$BACKUP_DIR"
            cp "$HOME/$file" "$BACKUP_DIR/"
        fi
        print_warning "Backed up existing $file to $BACKUP_DIR"
    fi
}

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    print_status "Updating existing installation..."
    if [ "$TEST_MODE" = false ]; then
        cd "$INSTALL_DIR"
        git pull origin main
    fi
else
    print_status "Cloning repository..."
    if [ "$TEST_MODE" = false ]; then
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"

        # Configure git credential helper to cache token for future operations
        # This ensures auto-updates and manual pulls work without re-entering credentials
        git config credential.helper store
        print_status "Git credential helper configured for future updates"
    fi
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
    if [ -f "$file" ] || [ "$TEST_MODE" = true ]; then
        filename=$(basename "$file")
        # Skip . and ..
        if [ "$filename" != "." ] && [ "$filename" != ".." ]; then
            if [ "$TEST_MODE" = false ]; then
                ln -sf "$file" "$HOME/$filename"
            fi
            print_status "Linked $filename"
        fi
    fi
done

# Also handle non-hidden files in dotfiles directory
for file in "$INSTALL_DIR"/dotfiles/*; do
    if [ -f "$file" ] || [ "$TEST_MODE" = true ]; then
        filename=$(basename "$file")
        # Add dot prefix for home directory
        if [ "$TEST_MODE" = false ]; then
            ln -sf "$file" "$HOME/.$filename"
        fi
        print_status "Linked .$filename"
    fi
done

# Install scripts to ~/bin
print_status "Installing scripts..."
if [ "$TEST_MODE" = false ]; then
    mkdir -p "$HOME/bin"
fi
for script in "$INSTALL_DIR"/scripts/*; do
    if [ -f "$script" ] || [ "$TEST_MODE" = true ]; then
        scriptname=$(basename "$script")
        if [ "$TEST_MODE" = false ]; then
            ln -sf "$script" "$HOME/bin/$scriptname"
            chmod +x "$HOME/bin/$scriptname"
        fi
        print_status "Installed $scriptname"
    fi
done

# Add ~/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    if [ -f "$HOME/.bashrc" ]; then
        if [ "$TEST_MODE" = false ]; then
            echo '' >> "$HOME/.bashrc"
            echo '# Add ~/bin to PATH' >> "$HOME/.bashrc"
            echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.bashrc"
        fi
        print_status "Added ~/bin to PATH in .bashrc"
    fi
    if [ -f "$HOME/.zshrc" ]; then
        if [ "$TEST_MODE" = false ]; then
            echo '' >> "$HOME/.zshrc"
            echo '# Add ~/bin to PATH' >> "$HOME/.zshrc"
            echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.zshrc"
        fi
        print_status "Added ~/bin to PATH in .zshrc"
    fi
fi

# Setup auto-update via cron (optional)
print_status "Setting up auto-update..."
if [ "$TEST_MODE" = false ]; then
    CRON_CMD="0 */6 * * * cd $INSTALL_DIR && git pull origin main > /dev/null 2>&1"
    (crontab -l 2>/dev/null | grep -v "$INSTALL_DIR" ; echo "$CRON_CMD") | crontab -
fi
print_status "Auto-update scheduled (every 6 hours)"

# Create update script
if [ "$TEST_MODE" = false ]; then
    cat > "$HOME/bin/update-env-config" << 'UPDATESCRIPT'
#!/bin/bash
cd "$HOME/.environment-config" && git pull origin main
echo "Environment configuration updated!"
UPDATESCRIPT
    chmod +x "$HOME/bin/update-env-config"
fi
print_status "Created update-env-config command"

# Install Nerd Fonts
install_nerd_fonts() {
    echo ""
    echo -e "${BLUE}=============================================="
    echo "Nerd Font Installation"
    echo "==============================================\n${NC}"

    # Check if unzip is installed
    if ! command -v unzip &> /dev/null; then
        print_warning "unzip is not installed. Skipping font installation."
        echo "Install unzip with: sudo apt install unzip (Ubuntu/Debian)"
        return 1
    fi

    # Check if fontconfig is installed
    if ! command -v fc-cache &> /dev/null; then
        print_warning "fontconfig is not installed. Font cache will not be updated."
        echo "Install fontconfig with: sudo apt install fontconfig (Ubuntu/Debian)"
    fi

    # Create fonts directory
    FONTS_DIR="$HOME/.local/share/fonts"
    if [ "$TEST_MODE" = false ]; then
        mkdir -p "$FONTS_DIR/NerdFonts"
    fi
    print_status "Created fonts directory at $FONTS_DIR/NerdFonts"

    # Install Ubuntu Nerd Font
    FONT_ZIP="$INSTALL_DIR/fonts/Ubuntu.zip"
    if [ -f "$FONT_ZIP" ] || [ "$TEST_MODE" = true ]; then
        print_status "Installing Ubuntu Nerd Font..."
        if [ "$TEST_MODE" = false ]; then
            unzip -o "$FONT_ZIP" -d "$FONTS_DIR/NerdFonts" > /dev/null 2>&1
        fi
        print_status "Ubuntu Nerd Font installed"

        # Update font cache
        if command -v fc-cache &> /dev/null; then
            if [ "$TEST_MODE" = false ]; then
                fc-cache -f "$FONTS_DIR" > /dev/null 2>&1
            fi
            print_status "Font cache updated"
        fi
    else
        print_warning "Font file not found at $FONT_ZIP"
    fi

    echo ""
    echo -e "${GREEN}Nerd Fonts installation complete!${NC}"
    echo "The Ubuntu Nerd Font is now available for use with Starship and other applications."
    echo ""
}

# Install Oh-My-Zsh (optional)
install_ohmyzsh() {
    echo ""
    echo -e "${BLUE}=============================================="
    echo "Oh-My-Zsh Installation"
    echo "==============================================\n${NC}"

    # Check if zsh is installed
    if ! command -v zsh &> /dev/null; then
        echo "Zsh is not currently installed."
    else
        echo "Zsh is installed: $(zsh --version)"
    fi

    # Check if oh-my-zsh is already installed
    if [ -d "$HOME/.oh-my-zsh" ]; then
        print_status "Oh-My-Zsh is already installed"
        return 0
    fi

    # Ask user if they want to install oh-my-zsh
    echo ""
    echo "Would you like to install Oh-My-Zsh?"
    echo "This will install:"
    echo "  - Zsh (if not installed)"
    echo "  - Oh-My-Zsh framework"
    echo "  - Useful plugins (git, docker, python, etc.)"
    echo "  - zsh-autosuggestions & zsh-syntax-highlighting"
    echo "  - Agnoster theme"
    echo ""
    read -p "Install Oh-My-Zsh? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "$INSTALL_DIR/scripts/install-ohmyzsh.sh" ]; then
            print_status "Running Oh-My-Zsh installer..."
            bash "$INSTALL_DIR/scripts/install-ohmyzsh.sh"

            # Set zsh as default shell
            if command -v zsh &> /dev/null; then
                echo ""
                echo "Would you like to set Zsh as your default shell?"
                read -p "Set Zsh as default? (Y/n): " -n 1 -r
                echo

                if [[ $REPLY =~ ^[Nn]$ ]]; then
                    print_status "Keeping current default shell"
                else
                    ZSH_PATH=$(which zsh)
                    if [ -n "$ZSH_PATH" ]; then
                        print_status "Setting Zsh as default shell..."
                        if chsh -s "$ZSH_PATH"; then
                            print_status "Default shell changed to Zsh"
                            echo -e "${GREEN}You'll need to log out and back in for the change to take effect${NC}"
                        else
                            print_warning "Could not change default shell. You may need to run: chsh -s $ZSH_PATH"
                        fi
                    else
                        print_warning "Could not locate zsh binary"
                    fi
                fi
            fi
        else
            print_warning "Oh-My-Zsh installer script not found at $INSTALL_DIR/scripts/install-ohmyzsh.sh"
        fi
    else
        print_status "Skipping Oh-My-Zsh installation"
        echo "You can install it later by running: $HOME/bin/zsh-setup install"
    fi
}

echo ""
if [ "$TEST_MODE" = true ]; then
    echo -e "${BLUE}=============================================="
    echo "Test run complete!"
    echo "=============================================="
    echo ""
    echo -e "${YELLOW}No changes were made to your system.${NC}"
    echo "Run without --test flag to perform actual installation."
else
    # Run Nerd Font installation
    install_nerd_fonts

    # Run Oh-My-Zsh installation
    install_ohmyzsh

    echo ""
    echo -e "${GREEN}=============================================="
    echo "Installation complete!"
    echo "=============================================="
    echo ""
    echo "Next steps:"
    echo "1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo "2. Run 'update-env-config' anytime to pull latest changes"
    echo "3. Manage Zsh with: zsh-setup [status|themes|plugins|edit]"
    echo ""
    if [ -d "$BACKUP_DIR" ]; then
        echo "Your old configuration files are backed up in:"
        echo "$BACKUP_DIR"
        echo ""
    fi
fi
