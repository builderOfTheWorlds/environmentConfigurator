#!/usr/bin/env python3
"""
Claude Code Token Monitor for tmux status bar
Tracks token usage from Claude Code session files
Estimates rate limit pressure based on recent usage
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque

# Token limits by model (session context)
TOKEN_LIMITS = {
    "claude-sonnet-4-5-20250929": 200000,
    "claude-opus": 400000,
    "claude-haiku": 100000,
}

# Estimated rate limits (tokens per minute)
# Conservative estimates based on Pro plan
RATE_LIMIT_TPM = 40000  # tokens per minute threshold

# Cache file for tracking usage over time
CACHE_FILE = Path.home() / ".claude" / "token-rate-cache.json"

def get_current_session_id():
    """Get the most recent active Claude Code session ID"""
    claude_dir = Path.home() / ".claude"

    # Try to find the most recently modified session file
    projects_dir = claude_dir / "projects"
    if not projects_dir.exists():
        return None

    # Find all session .jsonl files
    session_files = []
    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            jsonl_files = list(project_dir.glob("*.jsonl"))
            jsonl_files = [f for f in jsonl_files if not f.name.startswith("agent-")]
            session_files.extend(jsonl_files)

    if not session_files:
        return None

    # Get the most recently modified file
    most_recent = max(session_files, key=lambda f: f.stat().st_mtime)

    # Check if it was modified in the last 10 minutes (active session)
    if datetime.now().timestamp() - most_recent.stat().st_mtime < 600:
        return most_recent

    return None

def parse_session_tokens_with_timestamps(session_file):
    """Parse token usage from a session file with timestamps"""
    if not session_file or not session_file.exists():
        return 0, 0, "unknown", []

    total_input = 0
    total_output = 0
    model = "unknown"
    usage_timeline = []  # List of (timestamp, tokens) tuples

    try:
        with open(session_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())

                    # Extract timestamp (ISO format string like "2025-11-11T21:13:53.415Z")
                    timestamp_str = data.get('timestamp', '')
                    timestamp = 0
                    if timestamp_str:
                        try:
                            # Parse ISO format timestamp
                            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            timestamp = dt.timestamp()
                        except:
                            pass

                    # Extract model name
                    if 'message' in data and isinstance(data['message'], dict):
                        if 'model' in data['message']:
                            model = data['message']['model']

                        # Extract token usage
                        if 'usage' in data['message']:
                            usage = data['message']['usage']
                            input_tok = usage.get('input_tokens', 0)
                            output_tok = usage.get('output_tokens', 0)
                            total_input += input_tok
                            total_output += output_tok

                            # Record this usage event
                            if timestamp and (input_tok + output_tok) > 0:
                                usage_timeline.append((timestamp, input_tok + output_tok))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return 0, 0, "unknown", []

    return total_input, total_output, model, usage_timeline

def calculate_rate_usage(usage_timeline):
    """Calculate tokens per minute over different time windows"""
    if not usage_timeline:
        return {"1min": 0, "5min": 0, "1hr": 0}

    now = datetime.now().timestamp()

    # Time windows in seconds
    windows = {
        "1min": 60,
        "5min": 300,
        "1hr": 3600
    }

    rates = {}
    for window_name, window_seconds in windows.items():
        cutoff_time = now - window_seconds
        # Sum tokens used within this time window
        tokens_in_window = sum(tokens for ts, tokens in usage_timeline if ts >= cutoff_time)
        # Calculate tokens per minute
        actual_duration = min(window_seconds, now - usage_timeline[0][0] if usage_timeline else window_seconds)
        tpm = (tokens_in_window / actual_duration) * 60 if actual_duration > 0 else 0
        rates[window_name] = int(tpm)

    return rates

def get_rate_status(rates):
    """Determine rate limit status and color"""
    # Use the highest rate (most restrictive)
    max_rate = max(rates.values()) if rates else 0

    percent = (max_rate / RATE_LIMIT_TPM) * 100

    if percent < 40:
        return "OK", "#[fg=#00ff00]", max_rate  # Green
    elif percent < 70:
        return "MOD", "#[fg=#ffff00]", max_rate  # Yellow
    elif percent < 90:
        return "HIGH", "#[fg=#ff8800]", max_rate  # Orange
    else:
        return "CRIT", "#[fg=#ff0000,bold]", max_rate  # Red

def format_token_display(used_tokens, total_tokens, rate_status, rate_color, rate_tpm):
    """Format token usage for tmux display with color coding"""
    if total_tokens == 0:
        return "Claude: Inactive"

    usage_percent = (used_tokens / total_tokens) * 100

    # Color coding for session tokens based on usage percentage
    if usage_percent < 50:
        session_color = "#[fg=#00ff00,bg=#000000]"
    elif usage_percent < 75:
        session_color = "#[fg=#ffff00,bg=#000000]"
    elif usage_percent < 90:
        session_color = "#[fg=#ff8800,bg=#000000]"
    else:
        session_color = "#[fg=#ff0000,bg=#000000,bold]"

    # Format session tokens
    if used_tokens >= 1000:
        used_str = f"{used_tokens/1000:.1f}K"
    else:
        used_str = str(used_tokens)

    if total_tokens >= 1000:
        total_str = f"{total_tokens/1000:.0f}K"
    else:
        total_str = str(total_tokens)

    # Format rate
    if rate_tpm >= 1000:
        rate_str = f"{rate_tpm/1000:.1f}K"
    else:
        rate_str = str(rate_tpm)

    # Compact format: Session | Rate
    return f"{session_color}{used_str}/{total_str}#[default] | {rate_color}{rate_status} {rate_str}TPM#[default]"

def main():
    """Main function to get and display token usage"""
    session_file = get_current_session_id()

    if not session_file:
        print("Claude: Inactive")
        return

    input_tokens, output_tokens, model, usage_timeline = parse_session_tokens_with_timestamps(session_file)
    total_used = input_tokens + output_tokens

    # Determine token limit based on model
    token_limit = TOKEN_LIMITS.get(model, 200000)  # Default to Sonnet limit

    # Calculate rate usage
    rates = calculate_rate_usage(usage_timeline)
    rate_status, rate_color, rate_tpm = get_rate_status(rates)

    print(format_token_display(total_used, token_limit, rate_status, rate_color, rate_tpm))

if __name__ == "__main__":
    main()
