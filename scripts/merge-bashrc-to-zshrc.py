#!/usr/bin/env python3
"""
Merge .bashrc configuration entries into .zshrc, avoiding duplicates.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Set, Tuple
import argparse
from datetime import datetime


class ConfigMerger:
    def __init__(self, bashrc_path: str = None, zshrc_path: str = None, dry_run: bool = False):
        """
        Initialize the config merger.

        Args:
            bashrc_path: Path to .bashrc file (defaults to ~/.bashrc)
            zshrc_path: Path to .zshrc file (defaults to ~/.zshrc)
            dry_run: If True, don't make actual changes
        """
        self.home = Path.home()
        self.bashrc_path = Path(bashrc_path) if bashrc_path else self.home / '.bashrc'
        self.zshrc_path = Path(zshrc_path) if zshrc_path else self.home / '.zshrc'
        self.dry_run = dry_run

        # Marker to identify merged content
        self.marker_start = "# --- Merged from .bashrc ---"
        self.marker_end = "# --- End of .bashrc merge ---"

    def normalize_line(self, line: str) -> str:
        """Normalize a line for comparison (strip whitespace, ignore comments)."""
        # Remove leading/trailing whitespace
        normalized = line.strip()
        # Remove inline comments for comparison
        if '#' in normalized and not normalized.startswith('#'):
            normalized = normalized.split('#')[0].strip()
        return normalized

    def transform_to_zsh(self, entry: str) -> str:
        """
        Transform bash-specific syntax to zsh-compatible syntax.

        Args:
            entry: A bash configuration entry (single or multi-line)

        Returns:
            Zsh-compatible configuration entry
        """
        lines = entry.split('\n')
        transformed_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                transformed_lines.append(line)
                continue

            # Transform shopt commands to setopt
            # bash: shopt -s <option>  → zsh: setopt <option>
            # bash: shopt -u <option>  → zsh: unsetopt <option>
            shopt_match = re.match(r'^\s*shopt\s+(-[su])\s+(.+)', line)
            if shopt_match:
                flag, options = shopt_match.groups()
                opt_list = options.split()

                # Map bash shopt options to zsh setopt equivalents
                shopt_to_setopt = {
                    'histappend': 'append_history',
                    'cdspell': 'correct',
                    'nocaseglob': 'no_case_glob',
                    'extglob': 'extended_glob',
                    'dotglob': 'glob_dots',
                    'nullglob': 'null_glob',
                }

                zsh_opts = []
                for opt in opt_list:
                    zsh_opt = shopt_to_setopt.get(opt, opt)
                    if flag == '-s':
                        zsh_opts.append(f"setopt {zsh_opt}")
                    else:  # -u
                        zsh_opts.append(f"unsetopt {zsh_opt}")

                indent = len(line) - len(line.lstrip())
                transformed_lines.extend([' ' * indent + opt for opt in zsh_opts])
                continue

            # Transform PROMPT_COMMAND to precmd function
            # bash: PROMPT_COMMAND='command'  → zsh: precmd() { command }
            prompt_cmd_match = re.match(r'^\s*PROMPT_COMMAND=[\'"](.*)[\'"]', line)
            if prompt_cmd_match:
                command = prompt_cmd_match.group(1)
                indent = len(line) - len(line.lstrip())
                transformed_lines.append(' ' * indent + f"precmd() {{ {command} }}")
                continue

            # Transform bash completion to zsh completion
            # bash: complete -F function command  → zsh: compdef function command
            complete_match = re.match(r'^\s*complete\s+.*-F\s+(\S+)\s+(\S+)', line)
            if complete_match:
                func, cmd = complete_match.groups()
                indent = len(line) - len(line.lstrip())
                # Zsh needs completion system loaded
                transformed_lines.append(' ' * indent + f"compdef {func} {cmd}")
                continue

            # Replace bash-specific variables with zsh equivalents
            replacements = {
                'BASH_VERSION': 'ZSH_VERSION',
                'BASH_SOURCE': '${(%):-%x}',  # zsh equivalent for script path
                'BASHPID': '$$',
                'BASH_REMATCH': 'match',  # zsh regex capture
            }

            transformed_line = line
            for bash_var, zsh_var in replacements.items():
                # Match variable references like $BASH_VERSION or ${BASH_VERSION}
                transformed_line = re.sub(
                    rf'\${{\s*{bash_var}\s*}}',
                    zsh_var if zsh_var.startswith('$') else f'${{{zsh_var}}}',
                    transformed_line
                )
                transformed_line = re.sub(
                    rf'\${bash_var}\b',
                    zsh_var,
                    transformed_line
                )

            # Comment out bash-only builtins that don't have zsh equivalents
            bash_only_builtins = ['shopt', 'complete', 'compgen']
            for builtin in bash_only_builtins:
                if re.match(rf'^\s*{builtin}\s', stripped):
                    # If not already handled above, comment it out
                    if builtin == 'shopt' and shopt_match:
                        continue  # Already handled
                    if builtin == 'complete' and complete_match:
                        continue  # Already handled

                    indent = len(line) - len(line.lstrip())
                    transformed_line = ' ' * indent + f"# [bash-only] {stripped}"
                    break

            transformed_lines.append(transformed_line)

        return '\n'.join(transformed_lines)

    def is_significant_line(self, line: str) -> bool:
        """Check if a line contains significant configuration."""
        normalized = line.strip()

        # Skip empty lines
        if not normalized:
            return False

        # Skip pure comments
        if normalized.startswith('#'):
            return False

        # Skip common boilerplate
        boilerplate_patterns = [
            r'^\s*$',  # Empty lines
            r'^\s*#',  # Comments
            r'^\s*if\s+\[\s*-f\s+.*\]',  # Conditional sourcing guards
            r'^\s*fi\s*$',  # End of if
        ]

        for pattern in boilerplate_patterns:
            if re.match(pattern, line):
                return False

        return True

    def extract_config_entries(self, file_path: Path) -> List[str]:
        """Extract significant configuration entries from a file."""
        if not file_path.exists():
            return []

        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Keep track of multi-line statements
        config_blocks = []
        current_block = []
        in_function = False

        for line in lines:
            stripped = line.strip()

            # Track function definitions (multi-line)
            if re.match(r'^\s*function\s+\w+|^\s*\w+\s*\(\s*\)', line):
                in_function = True
                current_block = [line]
                continue

            if in_function:
                current_block.append(line)
                if stripped == '}':
                    in_function = False
                    config_blocks.append(''.join(current_block))
                    current_block = []
                continue

            # Skip insignificant lines
            if not self.is_significant_line(line):
                continue

            # Check for line continuation
            if stripped.endswith('\\'):
                current_block.append(line)
                continue

            if current_block:
                current_block.append(line)
                config_blocks.append(''.join(current_block))
                current_block = []
            else:
                config_blocks.append(line)

        return config_blocks

    def get_existing_configs(self, file_path: Path) -> Set[str]:
        """Get normalized versions of existing configs for duplicate detection."""
        configs = self.extract_config_entries(file_path)
        return {self.normalize_line(config) for config in configs}

    def find_new_entries(self) -> List[str]:
        """Find entries in .bashrc that don't exist in .zshrc."""
        bashrc_entries = self.extract_config_entries(self.bashrc_path)
        zshrc_normalized = self.get_existing_configs(self.zshrc_path)

        new_entries = []
        for entry in bashrc_entries:
            normalized = self.normalize_line(entry)
            if normalized and normalized not in zshrc_normalized:
                new_entries.append(entry)

        return new_entries

    def backup_zshrc(self) -> Path:
        """Create a backup of .zshrc."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.zshrc_path.parent / f'.zshrc.backup.{timestamp}'
        shutil.copy2(self.zshrc_path, backup_path)
        return backup_path

    def merge_configs(self) -> Tuple[int, List[str], List[str]]:
        """
        Merge configs from .bashrc to .zshrc.

        Returns:
            Tuple of (number of new entries, list of original entries, list of transformed entries)
        """
        if not self.bashrc_path.exists():
            raise FileNotFoundError(f".bashrc not found at {self.bashrc_path}")

        # Create .zshrc if it doesn't exist
        if not self.zshrc_path.exists():
            if not self.dry_run:
                self.zshrc_path.touch()

        # Find new entries
        new_entries = self.find_new_entries()

        if not new_entries:
            return 0, [], []

        # Transform entries for zsh
        transformed_entries = [self.transform_to_zsh(entry) for entry in new_entries]

        if self.dry_run:
            return len(new_entries), new_entries, transformed_entries

        # Backup before modifying
        backup_path = self.backup_zshrc()
        print(f"Backup created: {backup_path}")

        # Append new entries with transformations
        with open(self.zshrc_path, 'a') as f:
            f.write(f'\n{self.marker_start}\n')
            for transformed in transformed_entries:
                # Preserve original formatting
                if not transformed.endswith('\n'):
                    transformed += '\n'
                f.write(transformed)
            f.write(f'{self.marker_end}\n')

        return len(new_entries), new_entries, transformed_entries

    def remove_merged_section(self) -> bool:
        """Remove previously merged section from .zshrc."""
        if not self.zshrc_path.exists():
            return False

        with open(self.zshrc_path, 'r') as f:
            content = f.read()

        # Check if merged section exists
        if self.marker_start not in content:
            return False

        if self.dry_run:
            return True

        # Backup before modifying
        backup_path = self.backup_zshrc()
        print(f"Backup created: {backup_path}")

        # Remove merged section
        pattern = f'{re.escape(self.marker_start)}.*?{re.escape(self.marker_end)}\n?'
        new_content = re.sub(pattern, '', content, flags=re.DOTALL)

        with open(self.zshrc_path, 'w') as f:
            f.write(new_content)

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Merge .bashrc configuration into .zshrc, avoiding duplicates'
    )
    parser.add_argument(
        '--bashrc',
        help='Path to .bashrc file (default: ~/.bashrc)',
        default=None
    )
    parser.add_argument(
        '--zshrc',
        help='Path to .zshrc file (default: ~/.zshrc)',
        default=None
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be merged without making changes'
    )
    parser.add_argument(
        '--remove-merged',
        action='store_true',
        help='Remove previously merged section from .zshrc'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output'
    )

    args = parser.parse_args()

    merger = ConfigMerger(
        bashrc_path=args.bashrc,
        zshrc_path=args.zshrc,
        dry_run=args.dry_run
    )

    if args.remove_merged:
        removed = merger.remove_merged_section()
        if removed:
            status = "(dry-run)" if args.dry_run else ""
            print(f"Removed merged section from .zshrc {status}")
        else:
            print("No merged section found in .zshrc")
        return

    # Perform merge
    count, original_entries, transformed_entries = merger.merge_configs()

    if count == 0:
        print("No new entries to merge. .zshrc already contains all .bashrc configs.")
    else:
        status = "(dry-run)" if args.dry_run else ""
        print(f"Found {count} new entries to merge {status}")

        if args.verbose or args.dry_run:
            print("\n" + "=" * 70)
            for i, (orig, trans) in enumerate(zip(original_entries, transformed_entries), 1):
                print(f"\n[Entry {i}] Original (bash):")
                print("-" * 70)
                print(orig.rstrip())
                print(f"\n[Entry {i}] Transformed (zsh):")
                print("-" * 70)
                print(trans.rstrip())
                print("=" * 70)

        if not args.dry_run:
            print(f"\nSuccessfully merged {count} entries to {merger.zshrc_path}")
            print("Restart your shell or run: source ~/.zshrc")


if __name__ == '__main__':
    main()
