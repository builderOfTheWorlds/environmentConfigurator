"""
Centralized logging configuration for environment configurator.

Provides enterprise-level logging with:
- Multiple handlers (console, file, rotating file)
- Configurable log levels
- Structured log format
- Performance monitoring
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
from datetime import datetime


# Global logger configuration
_LOGGERS = {}
_LOG_DIR = Path.home() / ".config" / "environment-configurator" / "logs"
_DEFAULT_LOG_LEVEL = logging.INFO
_DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_VERBOSE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None,
    verbose: bool = False,
    enable_file_logging: bool = True,
) -> None:
    """
    Set up global logging configuration.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional specific log file path
        verbose: Enable verbose logging with file/line information
        enable_file_logging: Enable logging to file (in addition to console)
    """
    # Ensure log directory exists
    if enable_file_logging:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Choose format
    log_format = _VERBOSE_FORMAT if verbose else _DEFAULT_FORMAT
    formatter = logging.Formatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if enable_file_logging:
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = _LOG_DIR / f"env_configurator_{timestamp}.log"

        # Rotating file handler (10MB max, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: The name of the logger (typically __name__)
        log_level: Optional specific log level for this logger

    Returns:
        A configured logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting installation")
    """
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)

    if log_level is not None:
        logger.setLevel(log_level)

    _LOGGERS[name] = logger
    return logger


def set_log_level(level: int) -> None:
    """
    Change the log level for all loggers.

    Args:
        level: The new logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers:
        handler.setLevel(level)


def get_log_file_path() -> Path:
    """
    Get the current log file path.

    Returns:
        Path to the current log file
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    return _LOG_DIR / f"env_configurator_{timestamp}.log"


class LogContext:
    """
    Context manager for temporary log level changes.

    Example:
        >>> logger = get_logger(__name__)
        >>> with LogContext(logging.DEBUG):
        ...     logger.debug("This will be logged")
    """

    def __init__(self, level: int):
        """
        Initialize the log context.

        Args:
            level: The temporary logging level
        """
        self.level = level
        self.old_level: Optional[int] = None

    def __enter__(self) -> None:
        """Enter the context (set new log level)."""
        root_logger = logging.getLogger()
        self.old_level = root_logger.level
        set_log_level(self.level)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit the context (restore old log level)."""
        if self.old_level is not None:
            set_log_level(self.old_level)
