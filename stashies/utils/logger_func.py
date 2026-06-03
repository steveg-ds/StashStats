import logging
from logging.handlers import RotatingFileHandler


def create_logger(logger_name: str, log_file: str = None) -> logging.Logger:
    """
    Function to create basic logger
    - Parameters:
        - logger_name
        - log_file: optional path to write logs to file
    """

    # Create or get the logger
    logger = logging.getLogger(logger_name)

    # Only add handlers if this logger has no handlers configured
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
            fh.setFormatter(file_formatter)
            logger.addHandler(fh)

        logger.setLevel(logging.DEBUG)

    return logger
