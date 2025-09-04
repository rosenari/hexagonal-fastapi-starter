import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

# Context variable for request ID propagation
request_id_context: ContextVar[str] = ContextVar("request_id", default="N/A")


class RequestIDFilter(logging.Filter):
    """Filter that adds request_id to all log records from context variable."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            # Get request_id from context variable or record attribute
            record.request_id = getattr(record, "request_id", request_id_context.get())
        except Exception:
            record.request_id = "N/A"
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Always include these fields
        log_record["timestamp"] = datetime.fromtimestamp(
            record.created, timezone.utc
        ).isoformat()
        log_record["level"] = record.levelname
        log_record["name"] = record.name
        log_record["message"] = record.getMessage()
        log_record["request_id"] = getattr(record, "request_id", "N/A")
        
        # Add function and line info for debugging
        if record.levelno >= logging.WARNING:
            log_record["filename"] = record.filename
            log_record["lineno"] = record.lineno
            log_record["funcName"] = record.funcName


def setup_logging(log_level: str = "INFO") -> None:
    """Set up JSON logging configuration with request ID propagation."""
    
    # Create custom formatter
    formatter = CustomJsonFormatter()
    
    # Create request ID filter
    request_id_filter = RequestIDFilter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create and configure handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(request_id_filter)  # Add filter to inject request_id
    root_logger.addHandler(handler)
    
    # Suppress some noisy loggers in production
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)