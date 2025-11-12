#!/bin/bash
#
# Environment Configurator - Lightweight Installation Wrapper
# Version 2.0 - Now uses Python-based installer
#
# Usage:
#   Normal install: curl -fsSL https://raw.githubusercontent.com/builderOfTheWorlds/environmentConfigurator/main/install.sh | bash
#   Test mode: bash install.sh --test
#   Help: bash install.sh --help
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/builderOfTheWorlds/environmentConfigurator.git"
INSTALL_DIR="$HOME/.environment-config"
MIN_PYTHON_VERSION="3.8"

# Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "Please install Python 3.8 or higher first."
        exit 1
    fi

    # Check Python version
    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    local required_version="$MIN_PYTHON_VERSION"

    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python $python_version is installed, but Python $required_version or higher is required"
        exit 1
    fi

    print_success "Python $python_version found"
}

# Check Git
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        echo "Please install git first."
        exit 1
    fi
    print_success "Git found"
}

# Main installation
main() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Environment Configurator v2.0${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    # Check prerequisites
    print_info "Checking prerequisites..."
    check_python
    check_git

    # Clone or update repository
    if [ -d "$INSTALL_DIR" ]; then
        print_info "Updating existing installation..."
        cd "$INSTALL_DIR"
        git pull origin main || {
            print_warning "Could not update repository, continuing with existing version"
        }
    else
        print_info "Cloning repository..."
        git clone "$REPO_URL" "$INSTALL_DIR" || {
            print_error "Failed to clone repository"
            exit 1
        }
        cd "$INSTALL_DIR"
    fi

    # Install Python package and dependencies
    print_info "Installing Python package and dependencies..."

    # Try to use virtual environment if available, otherwise install user-level
    if command -v python3 -m venv &> /dev/null; then
        # Create venv if it doesn't exist
        if [ ! -d "$INSTALL_DIR/.venv" ]; then
            python3 -m venv "$INSTALL_DIR/.venv"
        fi
        source "$INSTALL_DIR/.venv/bin/activate"
        pip install --upgrade pip > /dev/null 2>&1
        pip install -e "$INSTALL_DIR" > /dev/null 2>&1 || {
            print_error "Failed to install Python package"
            exit 1
        }
    else
        # Install at user level
        python3 -m pip install --user --upgrade pip > /dev/null 2>&1
        python3 -m pip install --user -e "$INSTALL_DIR" > /dev/null 2>&1 || {
            print_error "Failed to install Python package"
            exit 1
        }
    fi

    print_success "Python package installed"

    # Run the Python installer
    print_info "Running environment configurator installer..."
    echo ""

    # Pass through command line arguments
    if [ -d "$INSTALL_DIR/.venv" ]; then
        source "$INSTALL_DIR/.venv/bin/activate"
        env-config install "$@"
    else
        python3 -m environment_configurator.cli.main install "$@"
    fi

    # Check exit code
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}Installation completed successfully!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
        echo "  2. Run 'env-config status' to check installation"
        echo "  3. Run 'tmux-theme-switcher list' to see available themes"
        echo "  4. Run 'env-config --help' for more commands"
        echo ""
    else
        echo ""
        print_error "Installation failed"
        echo "Check the logs for details."
        exit 1
    fi
}

# Show help
show_help() {
    cat << EOF
Environment Configurator - Installation Script v2.0

Usage: $0 [options]

Options:
  --test              Run in test mode (dry run, no changes)
  --no-fonts          Skip font installation
  --no-auto-update    Disable auto-update cron job
  --help, -h          Show this help message

Examples:
  $0                      # Normal installation
  $0 --test               # Test mode (dry run)
  $0 --no-fonts           # Skip font installation

For more information, visit:
  https://github.com/builderOfTheWorlds/environmentConfigurator

EOF
}

# Parse command line arguments
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Run main installation
main "$@"
