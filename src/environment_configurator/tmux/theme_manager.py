"""
Theme management for tmux.

Handles loading, filtering, and organizing themes.
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml

from environment_configurator.utils.logger import get_logger
from environment_configurator.tmux.models import Theme, ThemeCategory

logger = get_logger(__name__)


class ThemeManager:
    """Manages tmux themes."""

    def __init__(self, themes_file: Optional[Path] = None):
        """
        Initialize the theme manager.

        Args:
            themes_file: Path to themes YAML file (auto-detected if not provided)
        """
        if themes_file is None:
            # Auto-detect themes file
            themes_file = Path(__file__).parent.parent / "data" / "themes.yaml"

        self.themes_file = themes_file
        self.themes: List[Theme] = []
        self.categories: List[ThemeCategory] = []
        self._themes_by_category: Dict[str, List[Theme]] = {}

        # Load themes
        self._load_themes()

    def _load_themes(self) -> None:
        """Load themes from YAML file."""
        if not self.themes_file.exists():
            logger.error(f"Themes file not found: {self.themes_file}")
            return

        try:
            with open(self.themes_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Load categories
            if "categories" in data:
                for cat_data in data["categories"]:
                    category = ThemeCategory(
                        id=cat_data["id"],
                        display_name=cat_data["display_name"],
                        description=cat_data["description"],
                    )
                    self.categories.append(category)

            # Load themes
            if "themes" in data:
                for theme_data in data["themes"]:
                    theme = Theme(
                        name=theme_data["name"],
                        category=theme_data["category"],
                        description=theme_data["description"],
                        bg_color=theme_data["bg_color"],
                        fg_color=theme_data["fg_color"],
                        accent_color=theme_data["accent_color"],
                        border_color=theme_data["border_color"],
                        border_active=theme_data["border_active"],
                        inactive_bg=theme_data["inactive_bg"],
                        message_bg=theme_data["message_bg"],
                        message_fg=theme_data["message_fg"],
                        activity_color=theme_data["activity_color"],
                        dir_color=theme_data["dir_color"],
                        bat_theme=theme_data["bat_theme"],
                        ps1_color=theme_data["ps1_color"],
                        tags=theme_data.get("tags", []),
                    )
                    self.themes.append(theme)

                    # Organize by category
                    if theme.category not in self._themes_by_category:
                        self._themes_by_category[theme.category] = []
                    self._themes_by_category[theme.category].append(theme)

            logger.info(f"Loaded {len(self.themes)} themes in {len(self.categories)} categories")

        except Exception as e:
            logger.error(f"Failed to load themes: {e}")
            raise

    def get_all_themes(self) -> List[Theme]:
        """
        Get all themes.

        Returns:
            List of all themes
        """
        return self.themes.copy()

    def get_themes_by_category(self, category: str) -> List[Theme]:
        """
        Get themes filtered by category.

        Args:
            category: The category to filter by

        Returns:
            List of themes in the category
        """
        return self._themes_by_category.get(category, []).copy()

    def get_theme_by_name(self, name: str) -> Optional[Theme]:
        """
        Get a theme by its name.

        Args:
            name: The theme name

        Returns:
            Theme object or None if not found
        """
        for theme in self.themes:
            if theme.name.lower() == name.lower():
                return theme
        return None

    def search_themes(self, query: str) -> List[Theme]:
        """
        Search for themes by name or description.

        Args:
            query: The search query

        Returns:
            List of matching themes
        """
        query_lower = query.lower()
        matches = []

        for theme in self.themes:
            if (
                query_lower in theme.name.lower()
                or query_lower in theme.description.lower()
                or query_lower in theme.category.lower()
            ):
                matches.append(theme)

        return matches

    def get_categories(self) -> List[ThemeCategory]:
        """
        Get all theme categories.

        Returns:
            List of theme categories
        """
        return self.categories.copy()

    def get_grouped_themes(self) -> Dict[str, List[Theme]]:
        """
        Get themes grouped by category.

        Returns:
            Dictionary mapping category names to theme lists
        """
        return self._themes_by_category.copy()

    def get_theme_count(self) -> int:
        """
        Get the total number of themes.

        Returns:
            Number of themes
        """
        return len(self.themes)

    def get_category_count(self) -> int:
        """
        Get the total number of categories.

        Returns:
            Number of categories
        """
        return len(self.categories)
