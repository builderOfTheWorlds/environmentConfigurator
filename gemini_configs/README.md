# Gemini CLI Configuration Directory

This directory contains all Gemini CLI custom configurations and analysis scripts, version-controlled with git and symlinked to `~/.gemini/` for Gemini CLI to use.

## Directory Structure

```
gemini_configs/
├── INSTRUCTIONS.md                # Custom instructions loaded at every conversation start
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

All config files in this directory are **symlinked** from `~/.gemini/`:

```
~/.gemini/INSTRUCTIONS.md                     -> /path/to/project/gemini_configs/INSTRUCTIONS.md
~/.gemini/daily_analysis.py             -> /path/to/project/gemini_configs/analysis_scripts/daily_analysis.py
~/.gemini/run_analysis_if_inactive.sh   -> /path/to/project/gemini_configs/analysis_scripts/run_analysis_if_inactive.sh
```

This allows:
- ✅ Version control of Gemini configurations
- ✅ Sync configs across machines via git
- ✅ Gemini CLI reads from expected locations (`~/.gemini/`)
- ✅ Easy backup and portability

### Daily Analysis

**Schedule:** Runs every day at 5:00 AM (via cron)
**Condition:** Only if inactive for >1 hour (checks `history.jsonl` modification time)

```bash
# Cron job
0 5 * * * /home/matt/.gemini/run_analysis_if_inactive.sh
```

**What it analyzes:**
- Main conversation history (~/.gemini/history.jsonl)
- Project-specific conversations (~/.gemini/projects/*/)
- Task frequency, communication style, tech stack
- Pain points, preferences, key quotes

**Output:**
- `~/.gemini/latest_analysis.txt` - Latest report
- `~/.gemini/analysis_logs/report_YYYYMMDD_HHMMSS.txt` - Dated archives
- `~/.gemini/analysis_logs/analysis_YYYYMMDD_HHMMSS.log` - Execution logs

## Management Script

**Location:** `./data/ai/gemini-config` (symlink to `gemini_configs/manage_configs.sh`)

### Commands

```bash
# Check current status
./data/ai/gemini-config status

# Edit custom instructions (INSTRUCTIONS.md)
./data/ai/gemini-config edit-instructions

# Edit analysis script
./data/ai/gemini-config edit-analysis

# Verify all symlinks are working
./data/ai/gemini-config verify

# Recreate all symlinks
./data/ai/gemini-config setup

# Check git status of configs
./data/ai/gemini-config git-status

# Commit config changes
./data/ai/gemini-config git-commit

# Show help
./data/ai/gemini-config help
```

## Configuration Files

### INSTRUCTIONS.md

**Purpose:** Custom instructions loaded at the start of every Gemini CLI conversation

**Contains:**
- Token efficiency strategy
- Communication preferences (direct, code-first, no documentation)
- Development environment details (Python, PyCharm, Docker, WSL/Windows)
- Code style requirements (modular, pytest, configurable)
- Debugging checklist (common pain points to check)
- Project setup patterns
- Performance considerations

**Updating:**
```bash
./data/ai/gemini-config edit-instructions
# Make changes
./data/ai/gemini-config git-commit
```

### Analysis Scripts

#### daily_analysis.py

Comprehensive conversation analyzer that processes:
- All conversations in `~/.gemini/history.jsonl`
- All project conversations in `~/.gemini/projects/*/`
- Generates detailed reports on task frequency, communication style, tech stack, pain points

#### run_analysis_if_inactive.sh

Cron wrapper that:
1. Checks if `history.jsonl` was modified in last hour
2. If inactive >1 hour, runs `daily_analysis.py`
3. If active, skips analysis
4. Logs all activity to `~/.gemini/analysis_logs/cron_*.log`

## Git Workflow

### Making Config Changes

1. **Edit configs** (always in project directory):
   ```bash
   ./data/ai/gemini-config edit-instructions
   # or edit directly
   nano gemini_configs/INSTRUCTIONS.md
   ```

2. **Check what changed**:
   ```bash
   ./data/ai/gemini-config git-status
   ```

3. **Commit changes**:
   ```bash
   ./data/ai/gemini-config git-commit
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
   ./data/ai/gemini-config setup
   ```

This will:
- Create all necessary symlinks from `~/.gemini/` to project
- Set executable permissions on scripts
- Verify everything is working

3. **Verify**:
   ```bash
   ./data/ai/gemini-config verify
   ./data/ai/gemini-config status
   ```

## Manual Analysis

Run analysis anytime:
```bash
python3 ~/.gemini/daily_analysis.py
# or via symlink
python3 /mnt/c/Users/matt/PycharmProjects/environmentConfigurator/gemini_configs/analysis_scripts/daily_analysis.py
```

View latest results:
```bash
cat ~/.gemini/latest_analysis.txt
# or
cat /mnt/c/Users/matt/PycharmProjects/environmentConfigurator/gemini_configs/logs/latest_analysis.txt
```

## Important Notes

### DO NOT Edit Files in ~/.gemini/

Files in `~/.gemini/` are **symlinks**. While editing them will work (changes go to project), it's better to:
- Use `./data/ai/gemini-config edit-instructions` for guided editing
- Edit files directly in `gemini_configs/` directory
- Ensures you're aware these are version-controlled

### Git Ignore

The following are **NOT** tracked in git (listed in `.gitignore`):
- `gemini_configs/logs/` - Runtime logs
- Analysis output files (generated, not configuration)

### Cron Job

Cron job is set per-machine, not synced via git. After setting up on a new machine:

```bash
# Check if cron job exists
crontab -l

# If not, add it:
echo "0 5 * * * /home/matt/.gemini/run_analysis_if_inactive.sh" | crontab -
```

## Troubleshooting

### Symlinks broken?

```bash
./data/ai/gemini-config verify
./data/ai/gemini-config setup
```

### Analysis not running?

Check cron job:
```bash
crontab -l
```

Check logs:
```bash
ls -lah ~/.gemini/analysis_logs/
tail ~/.gemini/analysis_logs/cron_*.log
```

### Gemini not reading INSTRUCTIONS.md?

Verify symlink:
```bash
ls -la ~/.gemini/INSTRUCTIONS.md
readlink ~/.gemini/INSTRUCTIONS.md
cat ~/.gemini/INSTRUCTIONS.md  # Should show content
```
