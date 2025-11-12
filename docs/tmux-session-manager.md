# Tmux Session Manager

A Python utility for managing tmux-resurrect backup files. This tool helps you keep your backup directory organized by automatically cleaning up old session snapshots while preserving the most recent ones.

## Features

- **List Sessions**: View all sessions with their backup counts and date ranges
- **Preview Cleanup**: See what would be deleted before making changes (dry-run mode)
- **Smart Cleanup**: Automatically keep the last N backups per session
- **Archive Mode**: Move old backups to an archive directory instead of deleting
- **Interactive CLI**: User-friendly menu for all operations
- **Configurable**: JSON-based configuration file
- **Restore Support**: Easy session restoration with tmux-resurrect integration

## Installation

### Manual Installation

1. Make the script executable:
```bash
chmod +x scripts/tmux-session-manager.py
```

2. Create a symlink in the bin directory:
```bash
ln -sf ../scripts/tmux-session-manager.py bin/tmux-session-manager
```

3. Ensure the bin directory is in your PATH, or call it directly:
```bash
# Direct call
./bin/tmux-session-manager

# Or if bin is in PATH
tmux-session-manager
```

### Quick Start

Once installed, run without arguments to launch the interactive menu:
```bash
tmux-session-manager
```

## Usage

### Interactive Mode (Recommended)

Launch the interactive menu by running without arguments:

```bash
tmux-session-manager
```

This will present you with a menu:

```
======================================================================
Tmux Session Manager - Interactive Menu
======================================================================
1. List all sessions
2. Preview cleanup (dry run)
3. Cleanup old backups
4. Restore session
5. View configuration
6. Edit configuration
7. Exit
======================================================================
```

### Command-Line Mode

#### List All Sessions

```bash
tmux-session-manager list
```

Example output:
```
Tmux Session Backups Summary:
======================================================================
Session Name                   Snapshots    Oldest          Newest
----------------------------------------------------------------------
ashiorid_ai_manager            50           2025-11-06 22:48 2025-11-08 15:51
environmentConfigurator        51           2025-11-10 15:08 2025-11-11 22:09
sugartalking                   13           2025-11-08 17:52 2025-11-09 00:37
...
----------------------------------------------------------------------
Total: 12 sessions, 147 backup files
======================================================================
```

#### Preview Cleanup (Dry Run)

See what would be deleted without making any changes:

```bash
tmux-session-manager status
```

#### Clean Up Old Backups

With dry-run (preview only):
```bash
tmux-session-manager cleanup --dry-run
```

Actually perform cleanup:
```bash
tmux-session-manager cleanup
```

This will:
- Keep the last 10 backups per session (configurable)
- Archive or delete older backups based on configuration

#### Restore a Session

```bash
tmux-session-manager restore tmux_resurrect_20251111T220947.txt
```

#### View Configuration

```bash
tmux-session-manager config
```

## Configuration

Configuration is stored in `~/.config/tmux-session-manager/config.json`

### Default Configuration

```json
{
  "backup_dir": "backups/tmux-sessions",
  "keep_last_n": 10,
  "date_format": "%Y-%m-%d %H:%M:%S",
  "archive_deleted": true,
  "archive_dir": "backups/tmux-sessions/archive"
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backup_dir` | string | `backups/tmux-sessions` | Directory containing backup files |
| `keep_last_n` | integer | `10` | Number of backups to keep per session |
| `date_format` | string | `%Y-%m-%d %H:%M:%S` | Format for displaying dates |
| `archive_deleted` | boolean | `true` | Move deleted files to archive instead of deleting |
| `archive_dir` | string | `backups/tmux-sessions/archive` | Archive directory location |

### Editing Configuration

You can edit configuration in two ways:

1. **Interactive Mode**: Choose option 6 from the main menu
2. **Manual Edit**: Edit `~/.config/tmux-session-manager/config.json` directly

## How It Works

### Session Detection

The utility analyzes each backup file by reading the `state` line, which contains the active session name:

```
state	environmentConfigurator
```

### Timestamp Parsing

Filenames follow the format: `tmux_resurrect_YYYYMMDDTHHMMSS.txt`

Example: `tmux_resurrect_20251111T220947.txt` = 2025-11-11 22:09:47

### Cleanup Logic

For each session:
1. Sort all backups by timestamp (oldest first)
2. Keep the last N backups (default: 10)
3. Archive or delete the remaining older backups

Example: If `environmentConfigurator` has 51 backups:
- Keep the 10 most recent
- Archive/delete the 41 oldest

## Examples

### Example 1: Check Status Before Cleanup

```bash
# See current backup counts
tmux-session-manager list

# Preview what would be cleaned up
tmux-session-manager status

# Perform cleanup if satisfied
tmux-session-manager cleanup
```

### Example 2: Keep More Backups

```bash
# Launch interactive mode
tmux-session-manager

# Choose option 6 (Edit configuration)
# Choose option 2 (Change number of backups to keep)
# Enter: 20
```

### Example 3: Restore Old Session

```bash
# List all sessions to find the backup file
tmux-session-manager list

# Restore specific backup
tmux-session-manager restore tmux_resurrect_20251106T125800.txt
```

## Integration with tmux-resurrect

The utility is designed to work with tmux-resurrect plugin backups. To restore a session:

1. Use the restore command to get instructions
2. Create symlink to the backup file
3. Use tmux-resurrect's restore keybinding (prefix + Ctrl-r)

## Automation

You can automate cleanup with a cron job:

```bash
# Add to crontab to run daily at 3 AM
0 3 * * * /home/user/environmentConfigurator/bin/tmux-session-manager cleanup >> /var/log/tmux-cleanup.log 2>&1
```

## Troubleshooting

### "No backup files found"

- Check that `backup_dir` in config points to the correct location
- Verify backup files exist and match the naming pattern

### Configuration Not Saving

- Ensure `~/.config/tmux-session-manager/` directory is writable
- Check file permissions on `config.json`

### Cleanup Not Working

- Run with `--dry-run` first to preview changes
- Check that you have write permissions in the backup directory
- Verify `archive_dir` exists if archiving is enabled

## Safety Features

- **Dry-run mode**: Preview changes before making them
- **Archive mode**: Move files instead of deleting (enabled by default)
- **Confirmation prompts**: Interactive mode asks for confirmation
- **Per-session preservation**: Keeps backups for each session separately

## Current Statistics

Based on your current backups:

- **Total sessions**: 12 unique sessions
- **Total backups**: 147 files
- **Sessions with >10 backups**: 3 (ashiorid_ai_manager: 50, environmentConfigurator: 51, sugartalking: 13)
- **Cleanup potential**: 84 files can be archived/deleted to meet the 10-per-session limit

## Contributing

This utility is part of the environmentConfigurator project. To suggest improvements or report issues, please update the project documentation.
