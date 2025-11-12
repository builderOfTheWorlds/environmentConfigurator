#!/usr/bin/env python3
"""
Tmux Session Manager - Manage tmux-resurrect backup files

This utility helps manage tmux session backup files by:
- Listing sessions and their snapshot counts
- Cleaning up old backups while preserving the last N snapshots per session
- Restoring sessions from backups
- Providing an interactive CLI interface
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
import shutil


class Config:
    """Configuration management for tmux-session-manager"""

    DEFAULT_CONFIG = {
        "backup_dir": "backups/tmux-sessions",
        "keep_last_n": 10,
        "date_format": "%Y-%m-%d %H:%M:%S",
        "archive_deleted": True,
        "archive_dir": "backups/tmux-sessions/archive"
    }

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.config/tmux-session-manager/config.json")

        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.DEFAULT_CONFIG, **config}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"Configuration saved to {self.config_path}")

    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value

    def display(self):
        """Display current configuration"""
        print("\nCurrent Configuration:")
        print("=" * 50)
        for key, value in self.config.items():
            print(f"  {key:20s}: {value}")
        print("=" * 50)


class TmuxSessionManager:
    """Main class for managing tmux session backups"""

    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = Path(config.get("backup_dir"))
        self.keep_last_n = config.get("keep_last_n")

        if not self.backup_dir.exists():
            print(f"Warning: Backup directory '{self.backup_dir}' does not exist!")

    def get_session_from_file(self, filepath: Path) -> str:
        """Extract session name from backup file"""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.startswith('state'):
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            return parts[1]
        except IOError:
            pass
        return "unknown"

    def parse_timestamp_from_filename(self, filename: str) -> datetime:
        """Extract timestamp from filename like tmux_resurrect_20251106T125800.txt"""
        match = re.search(r'(\d{8}T\d{6})', filename)
        if match:
            timestamp_str = match.group(1)
            return datetime.strptime(timestamp_str, "%Y%m%dT%H%M%S")
        return datetime.min

    def get_backup_files(self) -> List[Path]:
        """Get all backup text files"""
        if not self.backup_dir.exists():
            return []
        return sorted(self.backup_dir.glob("tmux_resurrect_*.txt"))

    def analyze_backups(self) -> Dict[str, List[Tuple[Path, datetime]]]:
        """Analyze all backup files and group by session"""
        sessions = defaultdict(list)

        for backup_file in self.get_backup_files():
            session_name = self.get_session_from_file(backup_file)
            timestamp = self.parse_timestamp_from_filename(backup_file.name)
            sessions[session_name].append((backup_file, timestamp))

        # Sort each session's backups by timestamp (oldest first)
        for session in sessions:
            sessions[session].sort(key=lambda x: x[1])

        return sessions

    def list_sessions(self):
        """List all sessions with their backup counts"""
        sessions = self.analyze_backups()

        if not sessions:
            print("No backup files found.")
            return

        print("\nTmux Session Backups Summary:")
        print("=" * 70)
        print(f"{'Session Name':<30} {'Snapshots':<12} {'Oldest':<15} {'Newest':<15}")
        print("-" * 70)

        total_files = 0
        for session_name, backups in sorted(sessions.items()):
            count = len(backups)
            total_files += count
            oldest = backups[0][1].strftime("%Y-%m-%d %H:%M") if backups else "N/A"
            newest = backups[-1][1].strftime("%Y-%m-%d %H:%M") if backups else "N/A"
            print(f"{session_name:<30} {count:<12} {oldest:<15} {newest:<15}")

        print("-" * 70)
        print(f"Total: {len(sessions)} sessions, {total_files} backup files")
        print("=" * 70)

    def cleanup_preview(self) -> Dict[str, List[Path]]:
        """Preview what would be deleted without actually deleting"""
        sessions = self.analyze_backups()
        to_delete = {}

        for session_name, backups in sessions.items():
            if len(backups) > self.keep_last_n:
                # Keep the last N, delete the rest
                files_to_delete = [f[0] for f in backups[:-self.keep_last_n]]
                to_delete[session_name] = files_to_delete

        return to_delete

    def display_cleanup_preview(self):
        """Display what would be cleaned up"""
        to_delete = self.cleanup_preview()

        if not to_delete:
            print("\nNo files need to be cleaned up.")
            print(f"All sessions have {self.keep_last_n} or fewer backups.")
            return

        print("\nCleanup Preview (Dry Run):")
        print("=" * 70)
        print(f"Keeping last {self.keep_last_n} backups per session")
        print("-" * 70)

        total_to_delete = 0
        for session_name, files in sorted(to_delete.items()):
            total_to_delete += len(files)
            print(f"\n{session_name}: {len(files)} files to delete")
            for filepath in files:
                timestamp = self.parse_timestamp_from_filename(filepath.name)
                print(f"  - {filepath.name} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})")

        print("\n" + "=" * 70)
        print(f"Total files to delete: {total_to_delete}")
        print("=" * 70)

    def cleanup(self, dry_run: bool = True):
        """Clean up old backups, keeping last N per session"""
        to_delete = self.cleanup_preview()

        if not to_delete:
            print("\nNo files need to be cleaned up.")
            return

        if dry_run:
            self.display_cleanup_preview()
            return

        # Actual cleanup
        archive_enabled = self.config.get("archive_deleted", True)
        archive_dir = None

        if archive_enabled:
            archive_dir = Path(self.config.get("archive_dir"))
            archive_dir.mkdir(parents=True, exist_ok=True)
            print(f"\nArchiving deleted files to: {archive_dir}")

        deleted_count = 0
        archived_count = 0

        for session_name, files in to_delete.items():
            print(f"\nProcessing session: {session_name}")
            for filepath in files:
                try:
                    if archive_enabled:
                        # Move to archive
                        dest = archive_dir / filepath.name
                        shutil.move(str(filepath), str(dest))
                        archived_count += 1
                        print(f"  Archived: {filepath.name}")
                    else:
                        # Delete permanently
                        filepath.unlink()
                        deleted_count += 1
                        print(f"  Deleted: {filepath.name}")
                except Exception as e:
                    print(f"  Error processing {filepath.name}: {e}")

        print("\n" + "=" * 70)
        if archive_enabled:
            print(f"Cleanup complete! Archived {archived_count} files.")
        else:
            print(f"Cleanup complete! Deleted {deleted_count} files.")
        print("=" * 70)

    def restore_session(self, backup_file: str):
        """Restore a tmux session from a backup file"""
        filepath = self.backup_dir / backup_file

        if not filepath.exists():
            print(f"Error: Backup file '{backup_file}' not found!")
            return

        # Get session name
        session_name = self.get_session_from_file(filepath)
        timestamp = self.parse_timestamp_from_filename(filepath.name)

        print(f"\nRestore Session Information:")
        print("=" * 50)
        print(f"  File: {filepath.name}")
        print(f"  Session: {session_name}")
        print(f"  Timestamp: {timestamp.strftime(self.config.get('date_format'))}")
        print("=" * 50)

        # Check if tmux-resurrect is available
        resurrect_script = Path.home() / ".tmux/plugins/tmux-resurrect/scripts/restore.sh"

        if resurrect_script.exists():
            print("\nTo restore this session, run:")
            print(f"  ln -sf {filepath.absolute()} ~/.tmux/resurrect/last")
            print(f"  ~/.tmux/plugins/tmux-resurrect/scripts/restore.sh")
        else:
            print("\nTmux-resurrect not found. Manual restore instructions:")
            print(f"  1. Copy {filepath.name} to ~/.tmux/resurrect/")
            print(f"  2. Create symlink: ln -sf ~/.tmux/resurrect/{filepath.name} ~/.tmux/resurrect/last")
            print(f"  3. In tmux, press: prefix + Ctrl-r")


def interactive_menu(manager: TmuxSessionManager, config: Config):
    """Interactive CLI menu"""
    while True:
        print("\n" + "=" * 70)
        print("Tmux Session Manager - Interactive Menu")
        print("=" * 70)
        print("1. List all sessions")
        print("2. Preview cleanup (dry run)")
        print("3. Cleanup old backups")
        print("4. Restore session")
        print("5. View configuration")
        print("6. Edit configuration")
        print("7. Exit")
        print("=" * 70)

        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "1":
            manager.list_sessions()

        elif choice == "2":
            manager.display_cleanup_preview()

        elif choice == "3":
            manager.display_cleanup_preview()
            confirm = input("\nProceed with cleanup? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                manager.cleanup(dry_run=False)
            else:
                print("Cleanup cancelled.")

        elif choice == "4":
            manager.list_sessions()
            backup_file = input("\nEnter backup filename to restore: ").strip()
            if backup_file:
                manager.restore_session(backup_file)

        elif choice == "5":
            config.display()

        elif choice == "6":
            print("\nEdit Configuration:")
            print("1. Change backup directory")
            print("2. Change number of backups to keep")
            print("3. Toggle archive mode")
            print("4. Back to main menu")

            edit_choice = input("\nEnter choice (1-4): ").strip()

            if edit_choice == "1":
                new_dir = input(f"Enter new backup directory [{config.get('backup_dir')}]: ").strip()
                if new_dir:
                    config.set('backup_dir', new_dir)
                    config.save_config()

            elif edit_choice == "2":
                try:
                    new_n = int(input(f"Enter number of backups to keep [{config.get('keep_last_n')}]: ").strip())
                    if new_n > 0:
                        config.set('keep_last_n', new_n)
                        config.save_config()
                    else:
                        print("Number must be positive!")
                except ValueError:
                    print("Invalid number!")

            elif edit_choice == "3":
                current = config.get('archive_deleted')
                new_val = not current
                config.set('archive_deleted', new_val)
                config.save_config()
                print(f"Archive mode set to: {new_val}")

        elif choice == "7":
            print("\nExiting...")
            break

        else:
            print("\nInvalid choice! Please enter 1-7.")


def main():
    parser = argparse.ArgumentParser(
        description="Tmux Session Manager - Manage tmux-resurrect backup files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file (default: ~/.config/tmux-session-manager/config.json)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    subparsers.add_parser('list', help='List all sessions and their backup counts')

    # Status command (dry run)
    subparsers.add_parser('status', help='Show what would be cleaned up (dry run)')

    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without actually deleting files'
    )

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore a session from backup')
    restore_parser.add_argument('backup_file', help='Backup filename to restore')

    # Config command
    subparsers.add_parser('config', help='Show current configuration')

    # Interactive command
    subparsers.add_parser('interactive', help='Launch interactive menu')

    args = parser.parse_args()

    # Load configuration
    config = Config(args.config)
    manager = TmuxSessionManager(config)

    # If no command specified, launch interactive menu
    if not args.command:
        interactive_menu(manager, config)
        return

    # Execute command
    if args.command == 'list':
        manager.list_sessions()

    elif args.command == 'status':
        manager.display_cleanup_preview()

    elif args.command == 'cleanup':
        manager.cleanup(dry_run=args.dry_run)

    elif args.command == 'restore':
        manager.restore_session(args.backup_file)

    elif args.command == 'config':
        config.display()

    elif args.command == 'interactive':
        interactive_menu(manager, config)


if __name__ == '__main__':
    main()
