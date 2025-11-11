#!/bin/bash
# Wrapper script to run analysis only if user has been inactive for >1 hour

INACTIVITY_THRESHOLD=3600  # 1 hour in seconds
LOG_FILE="$HOME/.claude/analysis_logs/cron_$(date +%Y%m%d_%H%M%S).log"

# Create log directory if it doesn't exist
mkdir -p "$HOME/.claude/analysis_logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "======================================================"
log "Cron job started - checking for user inactivity"
log "======================================================"

# Check if history.jsonl was modified in the last hour
HISTORY_FILE="$HOME/.claude/history.jsonl"

if [ ! -f "$HISTORY_FILE" ]; then
    log "WARNING: History file not found at $HISTORY_FILE"
    log "Running analysis anyway..."
    python3 "$HOME/.claude/daily_analysis.py" 2>&1 | tee -a "$LOG_FILE"
    exit $?
fi

# Get last modification time of history file (seconds since epoch)
LAST_MODIFIED=$(stat -c %Y "$HISTORY_FILE" 2>/dev/null || stat -f %m "$HISTORY_FILE" 2>/dev/null)
CURRENT_TIME=$(date +%s)
INACTIVE_SECONDS=$((CURRENT_TIME - LAST_MODIFIED))

log "History file last modified: $(date -d @$LAST_MODIFIED '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r $LAST_MODIFIED '+%Y-%m-%d %H:%M:%S' 2>/dev/null)"
log "Current time: $(date '+%Y-%m-%d %H:%M:%S')"
log "Inactive for: $INACTIVE_SECONDS seconds ($((INACTIVE_SECONDS / 60)) minutes)"

if [ $INACTIVE_SECONDS -gt $INACTIVITY_THRESHOLD ]; then
    log "User has been inactive for >1 hour. Running analysis..."
    python3 "$HOME/.claude/daily_analysis.py" 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=$?
    log "Analysis completed with exit code: $EXIT_CODE"
    exit $EXIT_CODE
else
    log "User has been active recently (inactive for only $((INACTIVE_SECONDS / 60)) minutes)"
    log "Skipping analysis - will retry tomorrow"
    exit 0
fi
