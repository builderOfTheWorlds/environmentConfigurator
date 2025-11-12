# ========================================
# Environment Setup
# ========================================

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add cargo bin to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# ========================================
# Starship Prompt
# ========================================
eval "$(starship init zsh)"

# ========================================
# ZSH Plugins
# ========================================
# Fish-like autosuggestions
source ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

# Syntax highlighting (must be last)
source ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# ========================================
# Modern CLI Tools Configuration
# ========================================

# FZF Configuration
export FZF_DEFAULT_COMMAND='fd --type f --strip-cwd-prefix --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --strip-cwd-prefix --hidden --follow --exclude .git'

# FZF color scheme (catppuccin mocha)
export FZF_DEFAULT_OPTS=" \
--color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8 \
--color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc \
--color=marker:#f5e0dc,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8"

# Source FZF key bindings and completion
[ -f ~/.fzf/shell/key-bindings.zsh ] && source ~/.fzf/shell/key-bindings.zsh
[ -f ~/.fzf/shell/completion.zsh ] && source ~/.fzf/shell/completion.zsh

# Zoxide (smarter cd)
eval "$(zoxide init zsh)"

# ========================================
# Aliases - Modern Tool Replacements
# ========================================

# Use eza instead of ls
alias ls='eza --icons --group-directories-first'
alias ll='eza -l --icons --group-directories-first --git'
alias la='eza -la --icons --group-directories-first --git'
alias lt='eza --tree --level=2 --icons'
alias lta='eza --tree --level=2 --icons -a'

# Use bat instead of cat
alias cat='bat --style=auto'
alias less='bat --style=auto --paging=always'

# Use fd instead of find
alias find='fd'

# Use ripgrep instead of grep
alias grep='rg'

# Use zoxide instead of cd
alias cd='z'
alias cdi='zi'  # Interactive directory selection

# ========================================
# Additional Aliases
# ========================================

# Git shortcuts (enhanced with better tools)
alias gst='git status'
alias gd='git diff | bat --style=auto'
alias gl='git log --oneline --graph --decorate'
alias gla='git log --oneline --graph --decorate --all'

# Better defaults
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias mkdir='mkdir -p'

# ========================================
# History Configuration
# ========================================
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt SHARE_HISTORY
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_FIND_NO_DUPS
setopt HIST_SAVE_NO_DUPS

# ========================================
# ZSH Options
# ========================================
setopt AUTO_CD              # Auto change directory
setopt CORRECT              # Command correction
setopt AUTO_PUSHD           # Push directories onto stack
setopt PUSHD_IGNORE_DUPS    # Don't push duplicates
setopt EXTENDED_GLOB        # Extended globbing

# Case insensitive completion
autoload -Uz compinit && compinit
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' menu select

# ========================================
# Welcome Message
# ========================================
# echo "Welcome to your riced terminal!"
