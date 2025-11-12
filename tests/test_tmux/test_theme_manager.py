"""Tests for theme manager."""

from pathlib import Path
import pytest

from environment_configurator.tmux.theme_manager import ThemeManager
from environment_configurator.tmux.models import Theme


@pytest.fixture
def theme_manager() -> ThemeManager:
    """Create a theme manager instance."""
    return ThemeManager()


def test_load_themes(theme_manager: ThemeManager) -> None:
    """Test that themes are loaded."""
    assert len(theme_manager.get_all_themes()) > 0
    assert theme_manager.get_theme_count() > 0


def test_get_categories(theme_manager: ThemeManager) -> None:
    """Test getting theme categories."""
    categories = theme_manager.get_categories()
    assert len(categories) > 0

    # Check that we have expected categories
    category_ids = [cat.id for cat in categories]
    assert "green" in category_ids
    assert "blue" in category_ids


def test_get_theme_by_name(theme_manager: ThemeManager) -> None:
    """Test getting theme by name."""
    theme = theme_manager.get_theme_by_name("Matrix Green")
    assert theme is not None
    assert theme.name == "Matrix Green"
    assert theme.category == "green"


def test_get_nonexistent_theme(theme_manager: ThemeManager) -> None:
    """Test getting nonexistent theme."""
    theme = theme_manager.get_theme_by_name("Nonexistent Theme")
    assert theme is None


def test_get_themes_by_category(theme_manager: ThemeManager) -> None:
    """Test getting themes by category."""
    green_themes = theme_manager.get_themes_by_category("green")
    assert len(green_themes) > 0

    for theme in green_themes:
        assert theme.category == "green"


def test_search_themes(theme_manager: ThemeManager) -> None:
    """Test searching themes."""
    results = theme_manager.search_themes("green")
    assert len(results) > 0


def test_search_themes_no_results(theme_manager: ThemeManager) -> None:
    """Test searching with no results."""
    results = theme_manager.search_themes("nonexistentquery12345")
    assert len(results) == 0


def test_get_grouped_themes(theme_manager: ThemeManager) -> None:
    """Test getting grouped themes."""
    grouped = theme_manager.get_grouped_themes()
    assert isinstance(grouped, dict)
    assert len(grouped) > 0


def test_theme_model() -> None:
    """Test Theme model."""
    theme = Theme(
        name="Test Theme",
        category="test",
        description="Test description",
        bg_color="#000000",
        fg_color="#ffffff",
        accent_color="#ff0000",
        border_color="#00ff00",
        border_active="#0000ff",
        inactive_bg="#111111",
        message_bg="#222222",
        message_fg="#333333",
        activity_color="#444444",
        dir_color="01;32",
        bat_theme="TestTheme",
        ps1_color="\\[\\033[01;32m\\]",
    )

    assert theme.name == "Test Theme"
    assert str(theme) == "Test Theme (test)"

    # Test color swatches
    swatches = theme.get_color_swatches()
    assert "BG" in swatches
    assert swatches["BG"] == "#000000"

    # Test to_dict
    theme_dict = theme.to_dict()
    assert theme_dict["name"] == "Test Theme"
    assert theme_dict["bg_color"] == "#000000"
