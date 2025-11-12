"""
Environment Configurator - Enterprise-level dotfiles and environment management.

A comprehensive system for managing shell configurations, tmux themes, and
development environment setups across multiple machines.
"""

__version__ = "2.0.0"
__author__ = "Environment Configurator Team"
__license__ = "MIT"

from environment_configurator.utils.logger import get_logger

__all__ = ["get_logger", "__version__"]
