#!/bin/bash
# Claude Config Management Script
# Manages Claude Code configurations stored in this project and synced via git

PROJECT_DIR="/mnt/c/Users/matt/PycharmProjects/environmentConfigurator"
CONFIG_DIR="$PROJECT_DIR/claude_configs"
CLAUDE_HOME="$HOME/.claude"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}  Claude Config Management${NC}"
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

show_status() {
    print_header
    echo ""
    print_info "Config directory: $CONFIG_DIR"
    print_info "Claude home: $CLAUDE_HOME"
    echo ""
    echo "Symlinked configs:"

    ls -lah "$CLAUDE_HOME" 2>/dev/null | grep " -> .*environmentConfigurator" | while read -r line; do
        file=$(echo "$line" | awk '{print $9}')
        target=$(echo "$line" | awk '{print $11}')
        if [ -e "$CLAUDE_HOME/$file" ]; then
            print_success "$file -> ${target##*/}"
        else
            print_error "$file (broken symlink)"
        fi
    done

    echo ""
    echo "Config files in project:"
    find "$CONFIG_DIR" -type f \( -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.json" \) -exec basename {} \; | sort | while read -r file; do
        echo "  - $file"
    done
}

edit_claude_md() {
    print_info "Opening CLAUDE.md for editing..."
    ${EDITOR:-nano} "$CONFIG_DIR/CLAUDE.md"
    print_success "CLAUDE.md updated in project"
    print_warning "Remember to commit changes: cd $PROJECT_DIR && git add . && git commit -m 'Update CLAUDE.md config'"
}

edit_analysis_script() {
    print_info "Opening daily_analysis.py for editing..."
    ${EDITOR:-nano} "$CONFIG_DIR/analysis_scripts/daily_analysis.py"
    print_success "Analysis script updated in project"
    print_warning "Remember to commit changes: cd $PROJECT_DIR && git add . && git commit -m 'Update analysis script'"
}

verify_symlinks() {
    print_header
    print_info "Verifying symlinks..."
    echo ""

    errors=0

    # Check CLAUDE.md
    if [ -L "$CLAUDE_HOME/CLAUDE.md" ] && [ -e "$CLAUDE_HOME/CLAUDE.md" ]; then
        print_success "CLAUDE.md symlink OK"
    else
        print_error "CLAUDE.md symlink missing or broken"
        ((errors++))
    fi

    # Check scripts
    for script in daily_analysis.py run_analysis_if_inactive.sh analyze_conversation_history.py; do
        if [ -L "$CLAUDE_HOME/$script" ] && [ -e "$CLAUDE_HOME/$script" ]; then
            print_success "$script symlink OK"
        else
            print_error "$script symlink missing or broken"
            ((errors++))
        fi
    done

    echo ""
    if [ $errors -eq 0 ]; then
        print_success "All symlinks verified"
        return 0
    else
        print_error "Found $errors broken symlink(s)"
        print_info "Run '$0 setup' to recreate symlinks"
        return 1
    fi
}

setup_symlinks() {
    print_header
    print_info "Setting up symlinks from ~/.claude/ to project configs..."
    echo ""

    # Create symlinks
    ln -sf "$CONFIG_DIR/CLAUDE.md" "$CLAUDE_HOME/CLAUDE.md"
    print_success "Created CLAUDE.md symlink"

    ln -sf "$CONFIG_DIR/analysis_scripts/daily_analysis.py" "$CLAUDE_HOME/daily_analysis.py"
    print_success "Created daily_analysis.py symlink"

    ln -sf "$CONFIG_DIR/analysis_scripts/run_analysis_if_inactive.sh" "$CLAUDE_HOME/run_analysis_if_inactive.sh"
    print_success "Created run_analysis_if_inactive.sh symlink"

    ln -sf "$CONFIG_DIR/analysis_scripts/analyze_conversation_history.py" "$CLAUDE_HOME/analyze_conversation_history.py"
    print_success "Created analyze_conversation_history.py symlink"

    ln -sf "$CONFIG_DIR/ANALYSIS_RESULTS.md" "$CLAUDE_HOME/ANALYSIS_RESULTS.md"
    print_success "Created ANALYSIS_RESULTS.md symlink"

    # Ensure scripts are executable
    chmod +x "$CONFIG_DIR/analysis_scripts"/*.py
    chmod +x "$CONFIG_DIR/analysis_scripts"/*.sh
    print_success "Set executable permissions on scripts"

    echo ""
    print_success "Symlink setup complete"
}

git_status() {
    print_header
    print_info "Git status for configs:"
    echo ""
    cd "$PROJECT_DIR" || exit 1
    git status --short claude_configs/
}

git_commit() {
    print_header
    cd "$PROJECT_DIR" || exit 1

    if [ -z "$(git status --short claude_configs/)" ]; then
        print_info "No changes to commit"
        return 0
    fi

    print_info "Changes in claude_configs/:"
    git status --short claude_configs/
    echo ""

    read -p "Commit message: " message
    if [ -z "$message" ]; then
        print_error "Commit message cannot be empty"
        return 1
    fi

    git add claude_configs/
    git commit -m "$message"

    print_success "Changes committed"
    print_info "To push: cd $PROJECT_DIR && git push"
}

show_help() {
    print_header
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status          Show current configuration status"
    echo "  edit-claude     Edit CLAUDE.md custom instructions"
    echo "  edit-analysis   Edit daily analysis script"
    echo "  verify          Verify all symlinks are working"
    echo "  setup           Create/recreate all symlinks"
    echo "  git-status      Show git status of configs"
    echo "  git-commit      Commit config changes to git"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status                    # Check current config setup"
    echo "  $0 edit-claude               # Edit custom instructions"
    echo "  $0 git-commit                # Commit and sync changes"
}

# Main script logic
case "${1:-status}" in
    status)
        show_status
        ;;
    edit-claude)
        edit_claude_md
        ;;
    edit-analysis)
        edit_analysis_script
        ;;
    verify)
        verify_symlinks
        ;;
    setup)
        setup_symlinks
        ;;
    git-status)
        git_status
        ;;
    git-commit)
        git_commit
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
