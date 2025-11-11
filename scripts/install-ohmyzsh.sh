#!/bin/bash
# Oh-My-Zsh Installer Script
# Automated installation of Zsh and Oh-My-Zsh for deployment across environments

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}  Oh-My-Zsh Installer${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_zsh() {
    if command -v zsh &> /dev/null; then
        print_success "Zsh is already installed: $(zsh --version)"
        return 0
    else
        print_warning "Zsh is not installed"
        return 1
    fi
}

install_zsh() {
    print_info "Installing Zsh..."

    # Detect package manager and install
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y zsh
    elif command -v yum &> /dev/null; then
        sudo yum install -y zsh
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y zsh
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm zsh
    elif command -v brew &> /dev/null; then
        brew install zsh
    else
        print_error "Could not detect package manager. Please install zsh manually."
        exit 1
    fi

    if [ $? -eq 0 ]; then
        print_success "Zsh installed successfully"
    else
        print_error "Failed to install Zsh"
        exit 1
    fi
}

check_ohmyzsh() {
    if [ -d "$HOME/.oh-my-zsh" ]; then
        print_success "Oh-My-Zsh is already installed"
        return 0
    else
        print_warning "Oh-My-Zsh is not installed"
        return 1
    fi
}

install_ohmyzsh() {
    print_info "Installing Oh-My-Zsh..."

    # Download and install oh-my-zsh (unattended)
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

    if [ $? -eq 0 ]; then
        print_success "Oh-My-Zsh installed successfully"
    else
        print_error "Failed to install Oh-My-Zsh"
        exit 1
    fi
}

configure_zshrc() {
    print_info "Configuring .zshrc..."

    ZSHRC="$HOME/.zshrc"

    # Backup existing .zshrc if it exists and is not from oh-my-zsh
    if [ -f "$ZSHRC" ] && ! grep -q "oh-my-zsh" "$ZSHRC"; then
        cp "$ZSHRC" "$ZSHRC.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "Backed up existing .zshrc"
    fi

    # Set theme
    if [ -f "$ZSHRC" ]; then
        sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' "$ZSHRC" 2>/dev/null || \
        sed -i '' 's/ZSH_THEME="robbyrussell"/ZSH_THEME="agnoster"/' "$ZSHRC" 2>/dev/null
        print_success "Set theme to 'agnoster'"
    fi

    # Add useful plugins
    if [ -f "$ZSHRC" ]; then
        sed -i 's/plugins=(git)/plugins=(git docker docker-compose python pip kubectl sudo)/' "$ZSHRC" 2>/dev/null || \
        sed -i '' 's/plugins=(git)/plugins=(git docker docker-compose python pip kubectl sudo)/' "$ZSHRC" 2>/dev/null
        print_success "Enabled plugins: git, docker, docker-compose, python, pip, kubectl, sudo"
    fi

    # Add custom aliases
    cat >> "$ZSHRC" << 'EOF'

# Custom aliases
alias ll='ls -lah'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias gs='git status'
alias gp='git pull'
alias gc='git commit'
alias gd='git diff'

# Environment Configurator aliases (if in this project)
alias claude-config='$HOME/PycharmProjects/environmentConfigurator/bin/claude-config'
alias zsh-setup='$HOME/PycharmProjects/environmentConfigurator/bin/zsh-setup'
EOF

    print_success "Added custom aliases"
}

install_plugins() {
    print_info "Installing additional Zsh plugins..."

    ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

    # Install zsh-autosuggestions
    if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
        git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
        print_success "Installed zsh-autosuggestions"
    else
        print_info "zsh-autosuggestions already installed"
    fi

    # Install zsh-syntax-highlighting
    if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
        print_success "Installed zsh-syntax-highlighting"
    else
        print_info "zsh-syntax-highlighting already installed"
    fi

    # Update plugins in .zshrc
    ZSHRC="$HOME/.zshrc"
    if [ -f "$ZSHRC" ]; then
        # Add new plugins to existing list
        sed -i 's/plugins=(\(.*\))/plugins=(\1 zsh-autosuggestions zsh-syntax-highlighting)/' "$ZSHRC" 2>/dev/null || \
        sed -i '' 's/plugins=(\(.*\))/plugins=(\1 zsh-autosuggestions zsh-syntax-highlighting)/' "$ZSHRC" 2>/dev/null
        print_success "Enabled zsh-autosuggestions and zsh-syntax-highlighting plugins"
    fi
}

change_shell() {
    if [ "$SHELL" = "$(which zsh)" ]; then
        print_success "Zsh is already the default shell"
        return 0
    fi

    print_warning "Current shell is: $SHELL"
    echo -n "Change default shell to Zsh? (y/n): "
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        chsh -s "$(which zsh)"
        if [ $? -eq 0 ]; then
            print_success "Default shell changed to Zsh"
            print_warning "Please log out and log back in for the change to take effect"
        else
            print_error "Failed to change default shell"
            print_info "You may need to add $(which zsh) to /etc/shells first"
        fi
    else
        print_info "Keeping current shell. You can manually switch with: exec zsh"
    fi
}

main() {
    print_header
    echo ""

    # Check and install Zsh if needed
    if ! check_zsh; then
        install_zsh
    fi

    echo ""

    # Check and install Oh-My-Zsh if needed
    if ! check_ohmyzsh; then
        install_ohmyzsh
    fi

    echo ""

    # Configure .zshrc
    configure_zshrc

    echo ""

    # Install additional plugins
    install_plugins

    echo ""

    # Offer to change default shell
    change_shell

    echo ""
    print_header
    print_success "Oh-My-Zsh installation complete!"
    echo ""
    print_info "To start using Zsh now, run: exec zsh"
    print_info "To customize further, edit: ~/.zshrc"
    echo ""
}

# Run main installation
main
