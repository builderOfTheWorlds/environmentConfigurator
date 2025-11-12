"""
Font installation management.

Handles installation of Nerd Fonts for terminal theming.
"""

import zipfile
from pathlib import Path
from typing import Optional

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.file_utils import ensure_directory
from environment_configurator.utils.shell_utils import is_command_available, run_command

logger = get_logger(__name__)


class FontInstaller:
    """Manages installation of fonts."""

    def __init__(
        self,
        source_dir: Path,
        fonts_dir: Optional[Path] = None,
        test_mode: bool = False,
    ):
        """
        Initialize the font installer.

        Args:
            source_dir: Directory containing font files
            fonts_dir: Target directory for fonts (default: ~/.local/share/fonts/NerdFonts)
            test_mode: Whether running in test mode (no actual changes)
        """
        self.source_dir = source_dir / "fonts"
        self.test_mode = test_mode

        if fonts_dir is None:
            fonts_dir = Path.home() / ".local" / "share" / "fonts" / "NerdFonts"

        self.fonts_dir = fonts_dir

    def check_prerequisites(self) -> bool:
        """
        Check if required tools are available.

        Returns:
            True if all prerequisites are met, False otherwise
        """
        missing_tools = []

        if not is_command_available("unzip"):
            missing_tools.append("unzip")
            logger.warning("unzip is not installed - required for font installation")

        if not is_command_available("fc-cache"):
            logger.warning(
                "fontconfig is not installed - font cache will not be updated automatically"
            )

        if missing_tools:
            logger.error(
                f"Missing required tools: {', '.join(missing_tools)}. "
                f"Install with: sudo apt install {' '.join(missing_tools)}"
            )
            return False

        return True

    def install_from_zip(self, zip_path: Path) -> bool:
        """
        Install fonts from a ZIP archive.

        Args:
            zip_path: Path to the font ZIP file

        Returns:
            True if installation successful, False otherwise
        """
        if not zip_path.exists():
            logger.error(f"Font ZIP not found: {zip_path}")
            return False

        if self.test_mode:
            logger.info(f"[TEST MODE] Would extract fonts from: {zip_path}")
            return True

        # Create fonts directory
        ensure_directory(self.fonts_dir)

        try:
            # Extract fonts
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Extract only .ttf and .otf files
                font_files = [
                    f
                    for f in zip_ref.namelist()
                    if f.lower().endswith((".ttf", ".otf")) and not f.startswith("__MACOSX")
                ]

                for font_file in font_files:
                    zip_ref.extract(font_file, self.fonts_dir)

            logger.info(f"Installed fonts from {zip_path.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to extract fonts from {zip_path}: {e}")
            return False

    def update_font_cache(self) -> bool:
        """
        Update the system font cache.

        Returns:
            True if cache updated successfully, False otherwise
        """
        if not is_command_available("fc-cache"):
            logger.warning("fc-cache not available, skipping font cache update")
            return False

        if self.test_mode:
            logger.info("[TEST MODE] Would update font cache")
            return True

        try:
            run_command(
                ["fc-cache", "-f", str(self.fonts_dir)],
                check=True,
                capture_output=True,
                timeout=30,
            )
            logger.info("Font cache updated")
            return True

        except Exception as e:
            logger.error(f"Failed to update font cache: {e}")
            return False

    def install_all(self) -> bool:
        """
        Install all fonts from the source directory.

        Returns:
            True if installation successful, False otherwise
        """
        if not self.check_prerequisites():
            logger.warning("Prerequisites not met, skipping font installation")
            return False

        if not self.source_dir.exists():
            logger.warning(f"Font directory not found: {self.source_dir}")
            return False

        # Find all ZIP files
        font_zips = list(self.source_dir.glob("*.zip"))

        if not font_zips:
            logger.warning("No font ZIP files found")
            return False

        success_count = 0

        for font_zip in font_zips:
            if self.install_from_zip(font_zip):
                success_count += 1

        # Update font cache if any fonts were installed
        if success_count > 0:
            self.update_font_cache()

        logger.info(f"Installed {success_count}/{len(font_zips)} font packages")
        return success_count > 0

    def list_installed_fonts(self) -> list[str]:
        """
        List currently installed Nerd Fonts.

        Returns:
            List of installed font names
        """
        if not self.fonts_dir.exists():
            return []

        fonts = []
        for font_file in self.fonts_dir.rglob("*.ttf"):
            fonts.append(font_file.stem)

        for font_file in self.fonts_dir.rglob("*.otf"):
            fonts.append(font_file.stem)

        return sorted(set(fonts))
