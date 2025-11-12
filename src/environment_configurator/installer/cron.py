"""
Cron job management for auto-updates.

Handles creation and management of cron jobs for automatic environment updates.
"""

import re
from pathlib import Path
from typing import List, Optional

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.shell_utils import is_command_available, run_command

logger = get_logger(__name__)


class CronManager:
    """Manages cron jobs for environment configurator."""

    def __init__(self, test_mode: bool = False):
        """
        Initialize the cron manager.

        Args:
            test_mode: Whether running in test mode (no actual changes)
        """
        self.test_mode = test_mode

    def is_cron_available(self) -> bool:
        """
        Check if cron is available on the system.

        Returns:
            True if cron is available, False otherwise
        """
        available = is_command_available("crontab")
        logger.debug(f"Cron available: {available}")
        return available

    def get_current_crontab(self) -> List[str]:
        """
        Get the current user's crontab entries.

        Returns:
            List of crontab lines
        """
        if not self.is_cron_available():
            return []

        try:
            returncode, stdout, stderr = run_command(
                ["crontab", "-l"],
                check=False,
                capture_output=True,
            )

            if returncode == 0:
                return [line for line in stdout.split("\n") if line.strip()]
            else:
                # No crontab yet (this is normal)
                if "no crontab" in stderr.lower():
                    return []
                else:
                    logger.warning(f"Error reading crontab: {stderr}")
                    return []

        except Exception as e:
            logger.error(f"Failed to read crontab: {e}")
            return []

    def has_auto_update_job(self, install_dir: Path) -> bool:
        """
        Check if auto-update cron job already exists.

        Args:
            install_dir: Installation directory to check for

        Returns:
            True if auto-update job exists, False otherwise
        """
        crontab = self.get_current_crontab()
        install_dir_str = str(install_dir)

        for line in crontab:
            if install_dir_str in line and "git pull" in line:
                logger.debug(f"Found existing auto-update job: {line}")
                return True

        return False

    def add_auto_update_job(
        self,
        install_dir: Path,
        schedule: str = "0 */6 * * *",
        branch: str = "main",
    ) -> bool:
        """
        Add a cron job for auto-updates.

        Args:
            install_dir: Installation directory to update
            schedule: Cron schedule (default: every 6 hours)
            branch: Git branch to pull from (default: main)

        Returns:
            True if job added successfully, False otherwise
        """
        if not self.is_cron_available():
            logger.warning("Cron not available, cannot add auto-update job")
            return False

        if self.has_auto_update_job(install_dir):
            logger.info("Auto-update job already exists")
            return True

        if self.test_mode:
            logger.info(f"[TEST MODE] Would add cron job: {schedule} - auto-update")
            return True

        try:
            # Get current crontab
            current_crontab = self.get_current_crontab()

            # Add new job
            comment = "# Environment configurator auto-update"
            job = f"{schedule} cd {install_dir} && git pull origin {branch} > /dev/null 2>&1"

            new_crontab = current_crontab + [comment, job]

            # Write new crontab
            crontab_content = "\n".join(new_crontab) + "\n"

            process = run_command(
                ["crontab", "-"],
                check=True,
                capture_output=True,
            )

            # Feed the crontab content via stdin
            import subprocess

            subprocess.run(
                ["crontab", "-"],
                input=crontab_content,
                text=True,
                check=True,
                capture_output=True,
            )

            logger.info(f"Added auto-update cron job: {schedule}")
            return True

        except Exception as e:
            logger.error(f"Failed to add cron job: {e}")
            return False

    def remove_auto_update_job(self, install_dir: Path) -> bool:
        """
        Remove auto-update cron job.

        Args:
            install_dir: Installation directory to remove jobs for

        Returns:
            True if job removed successfully, False otherwise
        """
        if not self.is_cron_available():
            logger.warning("Cron not available")
            return False

        if self.test_mode:
            logger.info("[TEST MODE] Would remove auto-update cron job")
            return True

        try:
            current_crontab = self.get_current_crontab()
            install_dir_str = str(install_dir)

            # Filter out auto-update jobs
            new_crontab = [
                line
                for line in current_crontab
                if not (install_dir_str in line and "git pull" in line)
                and not line.strip().startswith("# Environment configurator")
            ]

            if len(new_crontab) == len(current_crontab):
                logger.info("No auto-update job found to remove")
                return True

            # Write new crontab
            if new_crontab:
                crontab_content = "\n".join(new_crontab) + "\n"
                import subprocess

                subprocess.run(
                    ["crontab", "-"],
                    input=crontab_content,
                    text=True,
                    check=True,
                    capture_output=True,
                )
            else:
                # Remove crontab entirely if empty
                subprocess.run(["crontab", "-r"], check=True, capture_output=True)

            logger.info("Removed auto-update cron job")
            return True

        except Exception as e:
            logger.error(f"Failed to remove cron job: {e}")
            return False

    def list_jobs(self) -> List[str]:
        """
        List all cron jobs for the current user.

        Returns:
            List of cron job descriptions
        """
        return self.get_current_crontab()
