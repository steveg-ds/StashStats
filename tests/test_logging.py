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


def test_logger_level_default_warning(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    logger = create_logger(_fresh("t.lvl.default"))
    assert logger.level == logging.WARNING


def test_idempotent_no_duplicate_handlers():
    name = _fresh("t.idem")
    create_logger(name)
    create_logger(name)
    assert len(logging.getLogger(name).handlers) == 1


def test_db_logger_has_handlers():
    """db.py logger must have at least one handler (not be silent)."""
    # Importing db triggers module-level logger creation
    import logging
    # Clear first so we're not relying on a previous test run
    logging.getLogger("DBManager").handlers.clear()
    import importlib
    import stashies.db as db_mod
    importlib.reload(db_mod)
    db_logger = logging.getLogger("DBManager")
    assert len(db_logger.handlers) >= 1


def test_component_and_db_base_logger_inheritance():
    from stashies.components.base_component import BaseComponent
    from stashies.db import DBManager, PostgresPool
    
    # Assert they possess class-level LOGGER attribute
    assert hasattr(BaseComponent, "LOGGER")
    assert hasattr(DBManager, "LOGGER")
    assert hasattr(PostgresPool, "LOGGER")
    
    # Verify logger names are set correctly to class name
    assert BaseComponent.LOGGER.name == "BaseComponent"
    assert DBManager.LOGGER.name == "DBManager"
    assert PostgresPool.LOGGER.name == "PostgresPool"

