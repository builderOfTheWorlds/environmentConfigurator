# Claude Code Configuration Directory

This directory contains all Claude Code custom configurations and analysis scripts, version-controlled with git and symlinked to `~/.claude/` for Claude Code to use.

## Directory Structure

```
claude_configs/
├── CLAUDE.md                      # Custom instructions loaded at every conversation start
├── ANALYSIS_RESULTS.md            # Latest conversation history analysis results
├── analysis_scripts/
│   ├── daily_analysis.py          # Comprehensive daily conversation analyzer
│   ├── run_analysis_if_inactive.sh # Cron wrapper (checks 1hr inactivity)
│   └── analyze_conversation_history.py # Original analysis script
├── logs/                          # Analysis logs (git-ignored)
├── manage_configs.sh              # Config management utility
└── README.md                      # This file
```

## How It Works

### Symlink Architecture

All config files in this directory are **symlinked** from `~/.claude/`:

```
~/.claude/CLAUDE.md                     -> /path/to/project/claude_configs/CLAUDE.md
~/.claude/daily_analysis.py             -> /path/to/project/claude_configs/analysis_scripts/daily_analysis.py
~/.claude/run_analysis_if_inactive.sh   -> /path/to/project/claude_configs/analysis_scripts/run_analysis_if_inactive.sh
```

This allows:
- ✅ Version control of Claude configurations
- ✅ Sync configs across machines via git
- ✅ Claude Code reads from expected locations (`~/.claude/`)
- ✅ Easy backup and portability

### Daily Analysis

**Schedule:** Runs every day at 5:00 AM (via cron)
**Condition:** Only if inactive for >1 hour (checks `history.jsonl` modification time)

```bash
# Cron job
0 5 * * * /home/matt/.claude/run_analysis_if_inactive.sh
```

**What it analyzes:**
- Main conversation history (~/.claude/history.jsonl)
- Project-specific conversations (~/.claude/projects/*/)
- Task frequency, communication style, tech stack
- Pain points, preferences, key quotes

**Output:**
- `~/.claude/latest_analysis.txt` - Latest report
- `~/.claude/analysis_logs/report_YYYYMMDD_HHMMSS.txt` - Dated archives
- `~/.claude/analysis_logs/analysis_YYYYMMDD_HHMMSS.log` - Execution logs

## Management Script

**Location:** `./data/ai/claude-config` (symlink to `claude_configs/manage_configs.sh`)

### Commands

```bash
# Check current status
./data/ai/claude-config status

# Edit custom instructions (CLAUDE.md)
./data/ai/claude-config edit-claude

# Edit analysis script
./data/ai/claude-config edit-analysis

# Verify all symlinks are working
./data/ai/claude-config verify

# Recreate all symlinks
./data/ai/claude-config setup

# Check git status of configs
./data/ai/claude-config git-status

# Commit config changes
./data/ai/claude-config git-commit

# Show help
./data/ai/claude-config help
```

## Configuration Files

### CLAUDE.md

**Purpose:** Custom instructions loaded at the start of every Claude Code conversation

**Contains:**
- Token efficiency strategy (use Haiku agents for simple tasks)
- Communication preferences (direct, code-first, no documentation)
- Development environment details (Python, PyCharm, Docker, WSL/Windows)
- Code style requirements (modular, pytest, configurable)
- Debugging checklist (common pain points to check)
- Project setup patterns
- Performance considerations

**Updating:**
```bash
./data/ai/claude-config edit-claude
# Make changes
./data/ai/claude-config git-commit
```

### Analysis Scripts

#### daily_analysis.py

Comprehensive conversation analyzer that processes:
- All conversations in `~/.claude/history.jsonl`
- All project conversations in `~/.claude/projects/*/`
- Generates detailed reports on task frequency, communication style, tech stack, pain points

#### run_analysis_if_inactive.sh

Cron wrapper that:
1. Checks if `history.jsonl` was modified in last hour
2. If inactive >1 hour, runs `daily_analysis.py`
3. If active, skips analysis
4. Logs all activity to `~/.claude/analysis_logs/cron_*.log`

## Git Workflow

### Making Config Changes

1. **Edit configs** (always in project directory):
   ```bash
   ./data/ai/claude-config edit-claude
   # or edit directly
   nano claude_configs/CLAUDE.md
   ```

2. **Check what changed**:
   ```bash
   ./data/ai/claude-config git-status
   ```

3. **Commit changes**:
   ```bash
   ./data/ai/claude-config git-commit
   # Enter commit message
   ```

4. **Push to remote**:
   ```bash
   git push
   ```

### Syncing to New Machine

1. **Clone the environmentConfigurator repo**:
   ```bash
   git clone <repo-url>
   cd environmentConfigurator
   ```

2. **Run setup script**:
   ```bash
   ./data/ai/claude-config setup
   ```

This will:
- Create all necessary symlinks from `~/.claude/` to project
- Set executable permissions on scripts
- Verify everything is working

3. **Verify**:
   ```bash
   ./data/ai/claude-config verify
   ./data/ai/claude-config status
   ```

## Manual Analysis

Run analysis anytime:
```bash
python3 ~/.claude/daily_analysis.py
# or via symlink
python3 /mnt/c/Users/matt/PycharmProjects/environmentConfigurator/claude_configs/analysis_scripts/daily_analysis.py
```

View latest results:
```bash
cat ~/.claude/latest_analysis.txt
# or
cat /mnt/c/Users/matt/PycharmProjects/environmentConfigurator/claude_configs/logs/latest_analysis.txt
```

## Important Notes

### DO NOT Edit Files in ~/.claude/

Files in `~/.claude/` are **symlinks**. While editing them will work (changes go to project), it's better to:
- Use `./data/ai/claude-config edit-claude` for guided editing
- Edit files directly in `claude_configs/` directory
- Ensures you're aware these are version-controlled

### Git Ignore

The following are **NOT** tracked in git (listed in `.gitignore`):
- `claude_configs/logs/` - Runtime logs
- Analysis output files (generated, not configuration)

### Cron Job

Cron job is set per-machine, not synced via git. After setting up on a new machine:

```bash
# Check if cron job exists
crontab -l

# If not, add it:
echo "0 5 * * * /home/matt/.claude/run_analysis_if_inactive.sh" | crontab -
```

## Troubleshooting

### Symlinks broken?

```bash
./data/ai/claude-config verify
./data/ai/claude-config setup
```

### Analysis not running?

Check cron job:
```bash
crontab -l
```

Check logs:
```bash
ls -lah ~/.claude/analysis_logs/
tail ~/.claude/analysis_logs/cron_*.log
```

### Claude not reading CLAUDE.md?

Verify symlink:
```bash
ls -la ~/.claude/CLAUDE.md
readlink ~/.claude/CLAUDE.md
cat ~/.claude/CLAUDE.md  # Should show content
```

## References

- **Claude Code Docs:** https://code.claude.com/docs
- **CLAUDE.md Documentation:** https://code.claude.com/docs/en/memory.md
- **Project Repository:** /mnt/c/Users/matt/PycharmProjects/environmentConfigurator
