import json
import logging
from io import StringIO
from unittest.mock import patch

import pytest

from app.infrastructure.logging import setup_logging, get_logger


class TestJSONLogging:
    def test_setup_logging_configures_root_logger(self) -> None:
        setup_logging(log_level="INFO")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0
        
        # Check if the handler has JSON formatter
        handler = root_logger.handlers[0]
        from app.infrastructure.logging import CustomJsonFormatter
        assert isinstance(handler.formatter, CustomJsonFormatter)

    def test_logger_outputs_json_format(self) -> None:
        from app.infrastructure.logging import CustomJsonFormatter
        
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        formatter = CustomJsonFormatter()
        handler.setFormatter(formatter)
        
        logger = get_logger("test_logger")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        test_message = "Test log message"
        logger.info(test_message)
        
        log_output = log_stream.getvalue().strip()
        
        # Should be valid JSON
        log_data = json.loads(log_output)
        
        assert log_data["message"] == test_message
        assert log_data["level"] == "INFO"
        assert log_data["name"] == "test_logger"
        assert "timestamp" in log_data

    def test_logger_includes_extra_fields(self) -> None:
        from app.infrastructure.logging import CustomJsonFormatter
        
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        formatter = CustomJsonFormatter()
        handler.setFormatter(formatter)
        
        logger = get_logger("test_logger")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        extra_data = {"request_id": "123", "user_id": "456"}
        logger.info("Test message", extra=extra_data)
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["request_id"] == "123"
        assert log_data["user_id"] == "456"

    def test_get_logger_returns_configured_logger(self) -> None:
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    @pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR"])
    def test_different_log_levels(self, log_level: str) -> None:
        from app.infrastructure.logging import CustomJsonFormatter
        
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        formatter = CustomJsonFormatter()
        handler.setFormatter(formatter)
        
        logger = get_logger("test_logger")
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, log_level))
        
        getattr(logger, log_level.lower())("Test message")
        
        log_output = log_stream.getvalue().strip()
        log_data = json.loads(log_output)
        
        assert log_data["level"] == log_level