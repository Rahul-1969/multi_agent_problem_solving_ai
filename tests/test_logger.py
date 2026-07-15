"""Tests for utils/logger.py."""

import json
import logging
import sys
from unittest import mock

import pytest

from utils import logger


@pytest.fixture(autouse=True)
def _clean_logging_state(monkeypatch):
    """Reset global logging state before each test."""
    # Clear environment variables that influence logger configuration.
    for var in ("LOG_LEVEL", "LOG_FORMAT", "LOG_FILE"):
        monkeypatch.delenv(var, raising=False)

    root = logging.getLogger()

    # Remove all handlers from the root logger and reset its level.
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    root.setLevel(logging.NOTSET)

    # Reset noisy logger levels that setup_logging modifies.
    for name in (
        "httpx",
        "httpcore",
        "urllib3",
        "google",
        "google.auth",
        "google.generativeai",
        "multipart",
    ):
        logging.getLogger(name).setLevel(logging.NOTSET)

    # Reload the module so module-level constants pick up the clean env.
    import importlib

    importlib.reload(logger)

    yield

    # Clean up handlers and root level after the test as well.
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    root.setLevel(logging.NOTSET)


def test_module_constants_defaults():
    assert logger.LOG_LEVEL == "INFO"
    assert logger.LOG_FORMAT == "text"
    assert logger.LOG_FILE == ""


def test_module_constants_from_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FORMAT", "json")
    monkeypatch.setenv("LOG_FILE", "/tmp/app.log")

    import importlib

    importlib.reload(logger)

    assert logger.LOG_LEVEL == "DEBUG"
    assert logger.LOG_FORMAT == "json"
    assert logger.LOG_FILE == "/tmp/app.log"


def test_json_formatter_basic():
    formatter = logger._JsonFormatter()
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="hello world",
        args=(),
        exc_info=None,
    )
    record.created = 1700000000.0

    output = formatter.format(record)
    data = json.loads(output)

    assert data["timestamp"] == "2023-11-14T22:13:20"
    assert data["level"] == "INFO"
    assert data["name"] == "test.logger"
    assert data["message"] == "hello world"
    assert "exc_info" not in data


def test_json_formatter_with_exc_info():
    formatter = logger._JsonFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="failure",
            args=(),
            exc_info=sys.exc_info(),
        )

    output = formatter.format(record)
    data = json.loads(output)

    assert data["level"] == "ERROR"
    assert data["message"] == "failure"
    assert "exc_info" in data
    assert "ValueError: boom" in data["exc_info"]


def test_setup_logging_sets_root_level():
    root = logging.getLogger()
    root.handlers.clear()
    logger.setup_logging()
    assert root.level == logging.INFO


def test_setup_logging_respects_log_level_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    import importlib

    importlib.reload(logger)
    root = logging.getLogger()
    root.handlers.clear()
    logger.setup_logging()
    assert root.level == logging.DEBUG


def test_setup_logging_adds_stream_handler():
    root = logging.getLogger()
    root.handlers.clear()
    logger.setup_logging()
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)


def test_setup_logging_text_format(monkeypatch, capsys):
    monkeypatch.setenv("LOG_FORMAT", "text")
    import importlib

    importlib.reload(logger)
    logging.getLogger().handlers.clear()
    logger.setup_logging()

    log = logging.getLogger("test.text")
    log.info("hello text")

    captured = capsys.readouterr()
    assert "[INFO]" in captured.out
    assert "test.text" in captured.out
    assert "hello text" in captured.out


def test_setup_logging_json_format(monkeypatch, capsys):
    monkeypatch.setenv("LOG_FORMAT", "json")
    import importlib

    importlib.reload(logger)
    logging.getLogger().handlers.clear()
    logger.setup_logging()

    log = logging.getLogger("test.json")
    log.info("hello json")

    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["level"] == "INFO"
    assert data["name"] == "test.json"
    assert data["message"] == "hello json"


def test_setup_logging_adds_file_handler(tmp_path, monkeypatch):
    log_file = str(tmp_path / "app.log")
    monkeypatch.setenv("LOG_FILE", log_file)
    import importlib

    importlib.reload(logger)
    root = logging.getLogger()
    root.handlers.clear()
    logger.setup_logging()

    file_handlers = [h for h in root.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(file_handlers) == 1
    assert file_handlers[0].baseFilename == log_file


def test_setup_logging_no_file_handler_when_log_file_empty():
    root = logging.getLogger()
    root.handlers.clear()
    logger.setup_logging()
    file_handlers = [h for h in root.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(file_handlers) == 0


def test_setup_logging_suppresses_noisy_loggers():
    logging.getLogger().handlers.clear()
    logger.setup_logging()
    for name in (
        "httpx",
        "httpcore",
        "urllib3",
        "google",
        "google.auth",
        "google.generativeai",
        "multipart",
    ):
        assert logging.getLogger(name).level == logging.WARNING


def test_setup_logging_idempotent():
    root = logging.getLogger()
    root.handlers.clear()
    logger.setup_logging()
    first_handlers = root.handlers[:]
    logger.setup_logging()
    second_handlers = root.handlers[:]
    assert first_handlers == second_handlers


def test_setup_logging_does_not_call_basic_config():
    logging.getLogger().handlers.clear()
    with mock.patch("logging.basicConfig") as mock_basic_config:
        logger.setup_logging()
        mock_basic_config.assert_not_called()


def test_get_logger_returns_named_logger():
    log = logger.get_logger("my.module")
    assert isinstance(log, logging.Logger)
    assert log.name == "my.module"
