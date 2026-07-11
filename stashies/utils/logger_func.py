import logging
import os
from logging.handlers import RotatingFileHandler


def create_logger(logger_name: str, log_file: str = None) -> logging.Logger:
    """
    Factory for app loggers.
    - Adds StreamHandler with timestamps if not already configured.
    - Sets propagate=False to prevent double-output under gunicorn/Dash.
    - Respects LOG_LEVEL env var (default: WARNING).
    - Parameters:
        - logger_name: hierarchical name, e.g. 'Model', 'AppController'
        - log_file: optional path for RotatingFileHandler (Docker use)
    """
    logger = logging.getLogger(logger_name)
    logger.propagate = False  # always unconditional — even on cached logger retrieval

    if not logger.handlers:
        level_name = os.getenv("LOG_LEVEL", "WARNING").upper()
        level = getattr(logging, level_name, logging.WARNING)

        formatter = logging.Formatter(
            "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

        if log_file:
            file_formatter = logging.Formatter(
                "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
            fh.setFormatter(file_formatter)
            fh.setLevel(level)
            logger.addHandler(fh)

        logger.setLevel(level)

    return logger
