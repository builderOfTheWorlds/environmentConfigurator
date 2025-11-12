# Cron Manager

A comprehensive utility for managing cron jobs in your environment configuration setup.

## Overview

`cron-manager` provides an easy-to-use interface for managing scheduled tasks (cron jobs) on your system. It includes preset configurations for common tasks and allows you to add, remove, and manage custom jobs.

## Features

- **List Jobs**: View all current cron jobs with readable formatting
- **Status Check**: Check if known jobs (analysis, sync) are configured
- **Preset Jobs**: Quick setup for common tasks
- **Custom Jobs**: Add your own scheduled tasks
- **Backup/Restore**: Save and restore cron configurations
- **Safe Editing**: Direct crontab editing with warnings

## Installation

The `cron-manager` utility is installed automatically when you run the main `install.sh` script. It will be available in your PATH at `~/bin/cron-manager`.

## Usage

### Basic Commands

```bash
cron-manager status        # Show status of known jobs
cron-manager list          # List all current cron jobs
cron-manager add-preset    # Add preset jobs (recommended)
cron-manager add-custom    # Add a custom job
cron-manager remove        # Remove a specific job
cron-manager edit          # Edit crontab directly
cron-manager backup        # Backup current cron jobs
cron-manager restore       # Restore from backup
cron-manager help          # Show help message
```

## Preset Jobs

The cron-manager includes two preset jobs:

### 1. Daily Analysis Script
- **Schedule**: 5:00 AM daily
- **Purpose**: Analyzes Claude conversation history
- **Requirements**:
  - Claude configs set up via `claude-config setup`
  - Script at `~/.claude/run_analysis_if_inactive.sh`
- **Behavior**:
  - Checks if you've been inactive >1 hour
  - Runs Python analysis on conversations
  - Logs to `~/.claude/analysis_logs/`

### 2. Environment Config Sync
- **Schedule**: Every 6 hours
- **Purpose**: Keeps environment configs up to date
- **Location**: `~/.environment-config`
- **Behavior**: Runs `git pull origin main` to sync latest changes

## Quick Start

### Setup Recommended Jobs

```bash
# Check current status
cron-manager status

# Add both preset jobs (recommended)
cron-manager add-preset
# Then select option 3 (Both)
```

### View Current Jobs

```bash
# List all jobs with details
cron-manager list

# Quick status check
cron-manager status
```

### Add Custom Job

```bash
cron-manager add-custom
```

You'll be prompted for:
- Schedule (in cron format)
- Command to run
- Description (optional)

## Cron Schedule Format

Cron uses 5 fields to specify when to run a command:

```
MIN HOUR DAY MONTH WEEKDAY
```

### Common Examples

```bash
# Daily at 5:00 AM
0 5 * * *

# Every 30 minutes
*/30 * * * *

# Every 6 hours
0 */6 * * *

# Weekly on Sunday at midnight
0 0 * * 0

# Monday-Friday at 9:00 AM
0 9 * * 1-5

# First day of every month at 6:00 AM
0 6 1 * *
```

### Field Values

- **MIN**: 0-59
- **HOUR**: 0-23
- **DAY**: 1-31
- **MONTH**: 1-12
- **WEEKDAY**: 0-6 (0=Sunday)

### Special Characters

- `*` - Any value
- `*/n` - Every nth value
- `n-m` - Range from n to m
- `n,m` - Values n and m

## Backup and Restore

### Backup Current Jobs

```bash
cron-manager backup
```

Backups are saved to `~/.cron-backups/crontab-YYYYMMDD-HHMMSS.bak`

### Restore from Backup

```bash
cron-manager restore
```

You'll be shown available backups and can select one to restore.

## Examples

### Example 1: Setup Everything

```bash
# Install environment config
bash install.sh

# Check cron status
cron-manager status

# Add recommended jobs
cron-manager add-preset
# Select: 3 (Both)

# Verify setup
cron-manager list
```

### Example 2: Add Custom Backup Job

```bash
# Add custom job
cron-manager add-custom

# When prompted:
# Schedule: 0 2 * * 0
# Command: /home/user/bin/backup-script.sh
# Description: Weekly backup on Sunday at 2 AM
```

### Example 3: Remove Old Jobs

```bash
# List current jobs
cron-manager list

# Remove specific job
cron-manager remove
# Follow prompts to select job number

# Or clear all jobs
cron-manager clear
```

## Troubleshooting

### Cron Not Available

If you see "crontab command not found":
- Cron may not be installed on your system
- On WSL, cron may need to be started: `sudo service cron start`
- Some environments don't support cron (use alternative schedulers)

### Jobs Not Running

Check the following:
1. Verify job is listed: `cron-manager list`
2. Check if cron service is running: `service cron status`
3. Check script permissions: `ls -l ~/.claude/run_analysis_if_inactive.sh`
4. Review logs if specified in the cron command

### Script Not Found

For preset jobs:
- Daily Analysis: Run `claude-config setup` first
- Environment Sync: Run main `install.sh` first

## Integration with Other Tools

### Claude Config

```bash
# Setup Claude configs first
claude-config setup

# Then add cron job for daily analysis
cron-manager add-preset
# Select: 1 (Daily Analysis)
```

### Environment Updates

```bash
# Manual update
update-env-config

# Automated (every 6 hours via cron)
cron-manager add-preset
# Select: 2 (Environment Sync)
```

## Advanced Usage

### Direct Editing

```bash
# Edit crontab directly (advanced users)
cron-manager edit
```

**Warning**: Direct editing can break jobs if not done carefully. Use `backup` first!

### Scripting

```bash
# Backup before making changes
cron-manager backup

# Make changes via script
# ... your automation ...

# Restore if needed
cron-manager restore
```

## Files and Directories

- **Utility Location**: `~/bin/cron-manager`
- **Backups**: `~/.cron-backups/`
- **System Crontab**: Managed by `crontab` command

## Related Commands

- `crontab -l` - List cron jobs (raw format)
- `crontab -e` - Edit cron jobs directly
- `crontab -r` - Remove all cron jobs
- `update-env-config` - Manual environment update
- `claude-config` - Manage Claude configurations

## See Also

- [Claude Config Management](../claude_configs/README.md)
- [Environment Configurator](../README.md)
- [Install Script](../install.sh)

## Support

For issues or questions:
1. Check `cron-manager help`
2. Review this README
3. Check system logs: `grep CRON /var/log/syslog` (Linux)
4. Verify cron service status

## License

Part of the Environment Configurator project.
