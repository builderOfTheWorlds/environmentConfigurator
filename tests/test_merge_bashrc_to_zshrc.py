#!/usr/bin/env python3
"""
Tests for merge-bashrc-to-zshrc.py
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from merge_bashrc_to_zshrc import ConfigMerger


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_bashrc(temp_dir):
    """Create a sample .bashrc file."""
    bashrc = temp_dir / '.bashrc'
    content = """# Sample .bashrc
export PATH="$HOME/bin:$PATH"
export EDITOR=vim

# Aliases
alias ll='ls -la'
alias gs='git status'

# Function
function mkcd() {
    mkdir -p "$1" && cd "$1"
}

# Some conditional stuff
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
"""
    bashrc.write_text(content)
    return bashrc


@pytest.fixture
def sample_zshrc(temp_dir):
    """Create a sample .zshrc file."""
    zshrc = temp_dir / '.zshrc'
    content = """# Sample .zshrc
export PATH="$HOME/.local/bin:$PATH"
export EDITOR=vim

# Oh-My-Zsh config
ZSH_THEME="robbyrussell"

# Existing alias
alias gs='git status'
"""
    zshrc.write_text(content)
    return zshrc


@pytest.fixture
def empty_zshrc(temp_dir):
    """Create an empty .zshrc file."""
    zshrc = temp_dir / '.zshrc'
    zshrc.touch()
    return zshrc


class TestConfigMerger:
    def test_init_default_paths(self):
        """Test initialization with default paths."""
        merger = ConfigMerger()
        assert merger.bashrc_path == Path.home() / '.bashrc'
        assert merger.zshrc_path == Path.home() / '.zshrc'
        assert merger.dry_run is False

    def test_init_custom_paths(self, sample_bashrc, sample_zshrc):
        """Test initialization with custom paths."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(sample_zshrc),
            dry_run=True
        )
        assert merger.bashrc_path == sample_bashrc
        assert merger.zshrc_path == sample_zshrc
        assert merger.dry_run is True

    def test_normalize_line(self):
        """Test line normalization."""
        merger = ConfigMerger(dry_run=True)

        assert merger.normalize_line("  export PATH=/usr/bin  ") == "export PATH=/usr/bin"
        assert merger.normalize_line("alias ll='ls -la'  # List all") == "alias ll='ls -la'"
        assert merger.normalize_line("  # Just a comment  ") == "# Just a comment"

    def test_is_significant_line(self):
        """Test identification of significant lines."""
        merger = ConfigMerger(dry_run=True)

        # Significant lines
        assert merger.is_significant_line("export PATH=/usr/bin")
        assert merger.is_significant_line("alias ll='ls -la'")
        assert merger.is_significant_line("source ~/.bash_aliases")

        # Insignificant lines
        assert not merger.is_significant_line("")
        assert not merger.is_significant_line("   ")
        assert not merger.is_significant_line("# Just a comment")
        assert not merger.is_significant_line("  # Another comment")

    def test_extract_config_entries(self, sample_bashrc):
        """Test extraction of config entries from .bashrc."""
        merger = ConfigMerger(bashrc_path=str(sample_bashrc), dry_run=True)
        entries = merger.extract_config_entries(sample_bashrc)

        # Should extract exports, aliases, and functions
        assert any('export PATH' in entry for entry in entries)
        assert any('alias ll' in entry for entry in entries)
        assert any('alias gs' in entry for entry in entries)
        assert any('function mkcd' in entry for entry in entries)

    def test_get_existing_configs(self, sample_zshrc):
        """Test getting existing configs from .zshrc."""
        merger = ConfigMerger(zshrc_path=str(sample_zshrc), dry_run=True)
        existing = merger.get_existing_configs(sample_zshrc)

        # Should contain normalized versions
        assert 'export EDITOR=vim' in existing
        assert "alias gs='git status'" in existing

    def test_find_new_entries_with_overlap(self, sample_bashrc, sample_zshrc):
        """Test finding new entries when there's overlap."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(sample_zshrc),
            dry_run=True
        )
        new_entries = merger.find_new_entries()

        # Should not include duplicates
        assert not any('export EDITOR=vim' in entry for entry in new_entries)
        assert not any("alias gs='git status'" in entry for entry in new_entries)

        # Should include unique entries
        assert any('alias ll' in entry for entry in new_entries)
        assert any('function mkcd' in entry for entry in new_entries)

    def test_find_new_entries_empty_zshrc(self, sample_bashrc, empty_zshrc):
        """Test finding new entries when .zshrc is empty."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(empty_zshrc),
            dry_run=True
        )
        new_entries = merger.find_new_entries()

        # Should include all significant entries
        assert any('export PATH' in entry for entry in new_entries)
        assert any('export EDITOR' in entry for entry in new_entries)
        assert any('alias ll' in entry for entry in new_entries)
        assert any('alias gs' in entry for entry in new_entries)

    def test_dry_run_no_changes(self, sample_bashrc, sample_zshrc):
        """Test that dry-run doesn't modify files."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(sample_zshrc),
            dry_run=True
        )

        original_content = sample_zshrc.read_text()
        count, orig_entries, trans_entries = merger.merge_configs()

        assert count > 0  # Should find entries
        assert sample_zshrc.read_text() == original_content  # No changes

    def test_merge_configs_creates_backup(self, sample_bashrc, sample_zshrc, temp_dir):
        """Test that merge creates a backup."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(sample_zshrc),
            dry_run=False
        )

        merger.merge_configs()

        # Check for backup files
        backups = list(temp_dir.glob('.zshrc.backup.*'))
        assert len(backups) > 0

    def test_merge_configs_adds_markers(self, sample_bashrc, sample_zshrc):
        """Test that merge adds marker comments."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(sample_zshrc),
            dry_run=False
        )

        merger.merge_configs()
        content = sample_zshrc.read_text()

        assert merger.marker_start in content
        assert merger.marker_end in content

    def test_merge_configs_preserves_formatting(self, sample_bashrc, empty_zshrc):
        """Test that merge preserves original formatting."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(empty_zshrc),
            dry_run=False
        )

        merger.merge_configs()
        content = empty_zshrc.read_text()

        # Check that function formatting is preserved
        assert 'function mkcd()' in content or 'mkcd()' in content
        assert 'mkdir -p "$1" && cd "$1"' in content

    def test_remove_merged_section(self, sample_bashrc, sample_zshrc):
        """Test removing merged section."""
        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(sample_zshrc),
            dry_run=False
        )

        # First merge
        merger.merge_configs()
        assert merger.marker_start in sample_zshrc.read_text()

        # Then remove
        removed = merger.remove_merged_section()
        assert removed is True
        content = sample_zshrc.read_text()
        assert merger.marker_start not in content
        assert merger.marker_end not in content

    def test_remove_merged_section_not_present(self, sample_zshrc):
        """Test removing merged section when not present."""
        merger = ConfigMerger(
            zshrc_path=str(sample_zshrc),
            dry_run=False
        )

        removed = merger.remove_merged_section()
        assert removed is False

    def test_no_bashrc_raises_error(self, temp_dir, empty_zshrc):
        """Test that missing .bashrc raises error."""
        fake_bashrc = temp_dir / '.bashrc_nonexistent'
        merger = ConfigMerger(
            bashrc_path=str(fake_bashrc),
            zshrc_path=str(empty_zshrc)
        )

        with pytest.raises(FileNotFoundError):
            merger.merge_configs()

    def test_creates_zshrc_if_missing(self, sample_bashrc, temp_dir):
        """Test that .zshrc is created if it doesn't exist."""
        zshrc = temp_dir / '.zshrc'
        assert not zshrc.exists()

        merger = ConfigMerger(
            bashrc_path=str(sample_bashrc),
            zshrc_path=str(zshrc),
            dry_run=False
        )

        merger.merge_configs()
        assert zshrc.exists()

    def test_no_new_entries(self, temp_dir):
        """Test when all .bashrc entries already exist in .zshrc."""
        bashrc = temp_dir / '.bashrc'
        bashrc.write_text("export EDITOR=vim\nalias gs='git status'\n")

        zshrc = temp_dir / '.zshrc'
        zshrc.write_text("export EDITOR=vim\nalias gs='git status'\n")

        merger = ConfigMerger(
            bashrc_path=str(bashrc),
            zshrc_path=str(zshrc),
            dry_run=False
        )

        count, orig_entries, trans_entries = merger.merge_configs()
        assert count == 0
        assert len(orig_entries) == 0
        assert len(trans_entries) == 0

    def test_multiline_function_preserved(self, temp_dir):
        """Test that multi-line functions are preserved correctly."""
        bashrc = temp_dir / '.bashrc'
        bashrc.write_text("""
function complex_func() {
    local var1="value"
    local var2="another"
    echo "$var1 $var2"
}
""")

        zshrc = temp_dir / '.zshrc'
        zshrc.write_text("# Empty\n")

        merger = ConfigMerger(
            bashrc_path=str(bashrc),
            zshrc_path=str(zshrc),
            dry_run=False
        )

        merger.merge_configs()
        content = zshrc.read_text()

        # Check that function is preserved as a block
        assert 'function complex_func()' in content or 'complex_func()' in content
        assert 'local var1="value"' in content
        assert 'local var2="another"' in content
        assert '}' in content


class TestBashToZshTransformations:
    """Test bash to zsh syntax transformations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.merger = ConfigMerger(dry_run=True)

    def test_shopt_to_setopt_enable(self):
        """Test shopt -s conversion to setopt."""
        bash_line = "shopt -s histappend"
        result = self.merger.transform_to_zsh(bash_line)
        assert "setopt append_history" in result
        assert "shopt" not in result

    def test_shopt_to_setopt_disable(self):
        """Test shopt -u conversion to unsetopt."""
        bash_line = "shopt -u nocaseglob"
        result = self.merger.transform_to_zsh(bash_line)
        assert "unsetopt no_case_glob" in result
        assert "shopt" not in result

    def test_shopt_multiple_options(self):
        """Test shopt with multiple options."""
        bash_line = "shopt -s extglob dotglob"
        result = self.merger.transform_to_zsh(bash_line)
        assert "setopt extended_glob" in result
        assert "setopt glob_dots" in result

    def test_prompt_command_transformation(self):
        """Test PROMPT_COMMAND to precmd transformation."""
        bash_line = "PROMPT_COMMAND='echo test'"
        result = self.merger.transform_to_zsh(bash_line)
        assert "precmd() { echo test }" in result
        assert "PROMPT_COMMAND" not in result

    def test_bash_completion_transformation(self):
        """Test bash complete to zsh compdef transformation."""
        bash_line = "complete -F _git git"
        result = self.merger.transform_to_zsh(bash_line)
        assert "compdef _git git" in result
        assert "complete" not in result

    def test_bash_version_replacement(self):
        """Test BASH_VERSION to ZSH_VERSION replacement."""
        bash_line = 'if [ -n "$BASH_VERSION" ]; then'
        result = self.merger.transform_to_zsh(bash_line)
        assert "ZSH_VERSION" in result
        assert "BASH_VERSION" not in result

    def test_bash_source_replacement(self):
        """Test BASH_SOURCE to zsh equivalent."""
        bash_line = 'script_dir="${BASH_SOURCE[0]}"'
        result = self.merger.transform_to_zsh(bash_line)
        assert "BASH_SOURCE" not in result
        assert "${(%):-%x}" in result

    def test_bashpid_replacement(self):
        """Test BASHPID to $$ replacement."""
        bash_line = "echo $BASHPID"
        result = self.merger.transform_to_zsh(bash_line)
        assert "$$" in result
        assert "BASHPID" not in result

    def test_bash_only_builtin_commented(self):
        """Test that unhandled bash-only builtins are commented out."""
        bash_line = "compgen -W 'option1 option2' -- $cur"
        result = self.merger.transform_to_zsh(bash_line)
        assert result.strip().startswith("# [bash-only]")
        assert "compgen" in result

    def test_preserve_whitespace_indentation(self):
        """Test that indentation is preserved."""
        bash_line = "    shopt -s histappend"
        result = self.merger.transform_to_zsh(bash_line)
        assert result.startswith("    ")

    def test_preserve_comments(self):
        """Test that comments are preserved."""
        bash_line = "# This is a comment"
        result = self.merger.transform_to_zsh(bash_line)
        assert result == bash_line

    def test_preserve_regular_exports(self):
        """Test that regular export statements are unchanged."""
        bash_line = 'export PATH="$HOME/bin:$PATH"'
        result = self.merger.transform_to_zsh(bash_line)
        assert result == bash_line

    def test_preserve_regular_aliases(self):
        """Test that aliases are unchanged."""
        bash_line = 'alias ll="ls -la"'
        result = self.merger.transform_to_zsh(bash_line)
        assert result == bash_line

    def test_multiline_function(self):
        """Test multiline function preservation."""
        bash_func = """function mytest() {
    echo "test"
    return 0
}"""
        result = self.merger.transform_to_zsh(bash_func)
        # Functions should be preserved as-is
        assert "function mytest()" in result or "mytest()" in result
        assert 'echo "test"' in result

    def test_empty_lines_preserved(self):
        """Test that empty lines are preserved."""
        bash_line = "\n"
        result = self.merger.transform_to_zsh(bash_line)
        assert result == bash_line

    def test_mixed_transformations(self):
        """Test multiple transformations in multi-line entry."""
        bash_entry = """shopt -s histappend
export PATH="$HOME/bin:$PATH"
PROMPT_COMMAND='history -a'"""
        result = self.merger.transform_to_zsh(bash_entry)
        assert "setopt append_history" in result
        assert 'export PATH="$HOME/bin:$PATH"' in result
        assert "precmd() { history -a }" in result
        assert "shopt" not in result
        assert "PROMPT_COMMAND" not in result

    def test_transformation_in_merge(self, temp_dir):
        """Test that transformations are applied during merge."""
        bashrc = temp_dir / '.bashrc'
        bashrc.write_text("""shopt -s histappend
export PATH="$HOME/bin:$PATH"
PROMPT_COMMAND='echo "bash ready"'
""")

        zshrc = temp_dir / '.zshrc'
        zshrc.write_text("# Empty\n")

        merger = ConfigMerger(
            bashrc_path=str(bashrc),
            zshrc_path=str(zshrc),
            dry_run=False
        )

        merger.merge_configs()
        content = zshrc.read_text()

        # Check transformations applied
        assert "setopt append_history" in content
        assert "precmd() { echo \"bash ready\" }" in content
        assert "shopt" not in content
        assert "PROMPT_COMMAND" not in content
