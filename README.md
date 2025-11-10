# Environment Configurator

Automated dotfiles and environment setup for consistent configuration across multiple machines.

## Features

- Automated installation via curl
- Auto-sync with git repository every 6 hours
- Safe backup of existing configurations
- Easy update and uninstall scripts
- Includes:
  - Shell configurations (.bashrc, .zshrc)
  - Git configuration
  - Tmux configuration
  - Tmux theme switcher
  - Custom scripts

## Quick Install

Run this one-liner on any machine:

```bash
curl -fsSL https://raw.githubusercontent.com/YOURUSERNAME/YOURREPO/main/install.sh | bash
```

Replace `YOURUSERNAME` and `YOURREPO` with your actual GitHub username and repository name.

## What Gets Installed

### Dotfiles (~/.)
- `.bashrc` - Bash shell configuration
- `.zshrc` - Zsh shell configuration
- `.gitconfig` - Git configuration
- `.tmux.conf` - Tmux configuration

### Scripts (~/bin/)
- `tmux-theme-switcher.sh` - Switch between tmux themes
- `update-env-config` - Manual update command

### Auto-Update
A cron job is installed to pull updates from the git repository every 6 hours.

## Manual Update

To manually pull the latest configuration:

```bash
update-env-config
```

Or:

```bash
cd ~/.environment-config && git pull
```

## Uninstall

To remove all installed configurations:

```bash
curl -fsSL https://raw.githubusercontent.com/YOURUSERNAME/YOURREPO/main/uninstall.sh | bash
```

Or if already installed:

```bash
bash ~/.environment-config/uninstall.sh
```

## Directory Structure

```
.
├── dotfiles/           # Configuration files to be symlinked to ~/
│   ├── .bashrc
│   ├── .zshrc
│   ├── .gitconfig
│   └── .tmux.conf
├── scripts/            # Scripts to be installed to ~/bin/
│   └── tmux-theme-switcher.sh
├── bin/                # Additional binaries (optional)
├── install.sh          # Main installation script
├── uninstall.sh        # Uninstallation script
└── README.md           # This file
```

## Backups

Your existing configuration files are automatically backed up to:
```
~/.environment-config-backup-YYYYMMDD-HHMMSS/
```

## Customization

### Adding New Dotfiles

1. Add the file to the `dotfiles/` directory
2. Commit and push to GitHub
3. Run `update-env-config` on your machines

### Adding New Scripts

1. Add the script to the `scripts/` directory
2. Make it executable: `chmod +x scripts/your-script.sh`
3. Commit and push to GitHub
4. Run `update-env-config` on your machines

### Modifying Auto-Update Frequency

The default is every 6 hours. To change this, edit the cron schedule in `install.sh`:

```bash
CRON_CMD="0 */6 * * * ..."  # Change */6 to your preferred interval
```

## Setup for First-Time Repository Creation

1. Create a new repository on GitHub
2. Update the `REPO_URL` in `install.sh`:
   ```bash
   REPO_URL="https://github.com/YOURUSERNAME/YOURREPO.git"
   ```
3. Initialize and push:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Environment configurator"
   git branch -M main
   git remote add origin https://github.com/YOURUSERNAME/YOURREPO.git
   git push -u origin main
   ```

## Requirements

- Git
- Bash or Zsh shell
- Unix-like environment (Linux, macOS, WSL)

## Security Notes

- Never commit sensitive data (passwords, API keys, tokens)
- Review the `.gitignore` file to ensure sensitive files are excluded
- Consider using a private repository if your configs contain personal information
- Review scripts before running them via curl

## Troubleshooting

### Scripts not in PATH
Run: `source ~/.bashrc` or `source ~/.zshrc`

### Permission denied
Make scripts executable: `chmod +x ~/bin/*`

### Cron job not running
Check cron logs: `grep CRON /var/log/syslog` (Linux) or check `crontab -l`

## License

MIT License - Feel free to use and modify as needed.
