"""
Git authentication management.

Handles authentication for private repositories using tokens or credentials.
"""

import getpass
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from environment_configurator.utils.logger import get_logger
from environment_configurator.utils.shell_utils import run_command

logger = get_logger(__name__)


class GitAuthenticator:
    """Manages Git authentication for repository access."""

    def __init__(self, repo_url: str, use_password: bool = False):
        """
        Initialize the Git authenticator.

        Args:
            repo_url: The base repository URL (https://github.com/user/repo.git)
            use_password: Whether to use password authentication (deprecated)
        """
        self.repo_url = repo_url
        self.use_password = use_password
        self.authenticated_url: Optional[str] = None

    def is_public_repo(self) -> bool:
        """
        Check if the repository is publicly accessible.

        Returns:
            True if repository is public, False otherwise
        """
        try:
            returncode, _, _ = run_command(
                ["git", "ls-remote", self.repo_url, "HEAD"],
                check=False,
                capture_output=True,
                timeout=10,
            )
            is_public = returncode == 0
            logger.info(f"Repository is {'public' if is_public else 'private'}")
            return is_public
        except Exception as e:
            logger.warning(f"Could not check repository accessibility: {e}")
            return False

    def get_authenticated_url(self) -> str:
        """
        Get an authenticated URL for the repository.

        Returns:
            Authenticated repository URL

        Raises:
            ValueError: If authentication fails or is cancelled
        """
        # Check if repo is public first
        if self.is_public_repo():
            logger.info("Repository is public, no authentication needed")
            self.authenticated_url = self.repo_url
            return self.repo_url

        # Private repo - need authentication
        logger.info("Repository is private, authentication required")

        if self.use_password:
            return self._get_password_auth_url()
        else:
            return self._get_token_auth_url()

    def _get_token_auth_url(self) -> str:
        """
        Get token-authenticated URL.

        Returns:
            URL with token authentication

        Raises:
            ValueError: If token is empty or invalid
        """
        print("\n" + "=" * 60)
        print("GitHub Authentication Required")
        print("=" * 60)
        print("\nTo create a Personal Access Token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select scope: 'repo' (full control)")
        print("4. Copy the generated token")
        print("")

        token = getpass.getpass("GitHub Personal Access Token: ")

        if not token:
            raise ValueError("Token cannot be empty")

        # Parse URL and insert token
        parsed = urlparse(self.repo_url)
        authenticated_url = f"https://{token}@{parsed.netloc}{parsed.path}"

        self.authenticated_url = authenticated_url
        logger.info("Token authentication configured")
        return authenticated_url

    def _get_password_auth_url(self) -> str:
        """
        Get password-authenticated URL (deprecated).

        Returns:
            URL with password authentication

        Raises:
            ValueError: If credentials are empty
        """
        print("\n" + "=" * 60)
        print("WARNING: Username/password auth is deprecated on GitHub")
        print("=" * 60)
        print("Consider using a Personal Access Token instead.")
        print("")

        username = input("GitHub Username: ")
        password = getpass.getpass("GitHub Password: ")

        if not username or not password:
            raise ValueError("Username and password cannot be empty")

        # Parse URL and insert credentials
        parsed = urlparse(self.repo_url)
        authenticated_url = f"https://{username}:{password}@{parsed.netloc}{parsed.path}"

        self.authenticated_url = authenticated_url
        logger.info("Password authentication configured")
        return authenticated_url

    def configure_credential_helper(self, repo_path: Path) -> None:
        """
        Configure Git credential helper to cache credentials.

        This ensures that subsequent pulls/pushes don't require re-authentication.

        Args:
            repo_path: Path to the Git repository
        """
        try:
            run_command(
                ["git", "config", "credential.helper", "store"],
                cwd=repo_path,
                check=True,
            )
            logger.info("Git credential helper configured for future operations")
        except Exception as e:
            logger.warning(f"Could not configure credential helper: {e}")

    def test_authentication(self) -> Tuple[bool, str]:
        """
        Test if authentication is working.

        Returns:
            Tuple of (success, message)
        """
        if not self.authenticated_url:
            return False, "No authenticated URL configured"

        try:
            returncode, stdout, stderr = run_command(
                ["git", "ls-remote", self.authenticated_url, "HEAD"],
                check=False,
                capture_output=True,
                timeout=10,
            )

            if returncode == 0:
                logger.info("Authentication test successful")
                return True, "Authentication successful"
            else:
                logger.error(f"Authentication test failed: {stderr}")
                return False, f"Authentication failed: {stderr}"

        except Exception as e:
            logger.error(f"Authentication test error: {e}")
            return False, f"Authentication test error: {e}"
