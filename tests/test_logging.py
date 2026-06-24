import logging
import os
import pytest
from stashies.utils.logger_func import create_logger


def _fresh(name):
    """Clear any cached logger so tests are isolated."""
    log = logging.getLogger(name)
    log.handlers.clear()
    return name


def test_logger_has_stream_handler():
    logger = create_logger(_fresh("t.stream"))
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_logger_format_has_timestamp():
    logger = create_logger(_fresh("t.fmt"))
    handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    assert "%(asctime)s" in handler.formatter._fmt


def test_logger_propagate_false():
    logger = create_logger(_fresh("t.prop"))
    assert logger.propagate is False


def test_logger_level_env_debug(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    logger = create_logger(_fresh("t.lvl.debug"))
    assert logger.level == logging.DEBUG


def test_logger_level_env_info(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    logger = create_logger(_fresh("t.lvl.info"))
    assert logger.level == logging.INFO


def test_idempotent_no_duplicate_handlers():
    name = _fresh("t.idem")
    create_logger(name)
    create_logger(name)
    assert len(logging.getLogger(name).handlers) == 1
