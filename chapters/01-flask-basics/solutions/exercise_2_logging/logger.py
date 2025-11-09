"""
JSON-formatted logging system with request tracking
Provides structured logging for better observability
"""

import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
import uuid
from flask import g, request, has_request_context


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record):
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add request context if available
        if has_request_context():
            log_data['request_id'] = g.get('request_id', 'no-request-id')
            log_data['method'] = request.method
            log_data['path'] = request.path
            log_data['remote_addr'] = request.remote_addr

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class RequestIdFilter(logging.Filter):
    """Add request ID to all log records"""

    def filter(self, record):
        """Add request_id to log record"""
        if has_request_context():
            record.request_id = g.get('request_id', 'no-request-id')
        else:
            record.request_id = 'no-request-context'
        return True


def setup_logging(app):
    """Configure JSON logging for the application"""

    # Remove default Flask logging handlers
    app.logger.handlers = []

    # Set logging level from config
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    app.logger.setLevel(getattr(logging, log_level))

    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    console_handler.addFilter(RequestIdFilter())
    app.logger.addHandler(console_handler)

    # File handler with rotation
    if app.config.get('ENV') != 'testing':
        file_handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(RequestIdFilter())
        app.logger.addHandler(file_handler)

    # Error file handler for errors only
    error_handler = RotatingFileHandler(
        log_dir / 'error.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    error_handler.addFilter(RequestIdFilter())
    app.logger.addHandler(error_handler)

    # Log configuration
    app.logger.info(
        "Logging configured",
        extra={
            'extra_fields': {
                'log_level': log_level,
                'handlers': len(app.logger.handlers),
                'log_dir': str(log_dir.absolute())
            }
        }
    )

    return app.logger


def log_request(logger):
    """Log incoming request details"""
    if has_request_context():
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'extra_fields': {
                    'request_data': {
                        'method': request.method,
                        'path': request.path,
                        'query_params': dict(request.args),
                        'headers': dict(request.headers),
                        'remote_addr': request.remote_addr,
                        'user_agent': request.user_agent.string
                    }
                }
            }
        )


def log_response(logger, response, duration_ms=None):
    """Log response details"""
    if has_request_context():
        log_data = {
            'status_code': response.status_code,
            'content_length': response.content_length,
            'content_type': response.content_type
        }

        if duration_ms:
            log_data['duration_ms'] = duration_ms

        level = logging.INFO
        if response.status_code >= 500:
            level = logging.ERROR
        elif response.status_code >= 400:
            level = logging.WARNING

        logger.log(
            level,
            f"Request completed: {request.method} {request.path} - {response.status_code}",
            extra={'extra_fields': {'response_data': log_data}}
        )


class APILogger:
    """Enhanced logger for API endpoints"""

    def __init__(self, logger):
        self.logger = logger

    def log_api_call(self, endpoint, method, **kwargs):
        """Log API endpoint call with context"""
        self.logger.info(
            f"API call: {method} {endpoint}",
            extra={'extra_fields': {'api_call': kwargs}}
        )

    def log_database_query(self, query, duration_ms):
        """Log database query performance"""
        self.logger.debug(
            "Database query executed",
            extra={
                'extra_fields': {
                    'db_query': {
                        'query': str(query)[:500],  # Truncate long queries
                        'duration_ms': duration_ms
                    }
                }
            }
        )

    def log_cache_hit(self, key, hit=True):
        """Log cache access"""
        self.logger.debug(
            f"Cache {'hit' if hit else 'miss'}: {key}",
            extra={
                'extra_fields': {
                    'cache': {
                        'key': key,
                        'hit': hit
                    }
                }
            }
        )

    def log_external_api_call(self, service, endpoint, status_code, duration_ms):
        """Log external API calls"""
        self.logger.info(
            f"External API call: {service}",
            extra={
                'extra_fields': {
                    'external_api': {
                        'service': service,
                        'endpoint': endpoint,
                        'status_code': status_code,
                        'duration_ms': duration_ms
                    }
                }
            }
        )

    def log_business_event(self, event_type, **data):
        """Log business-level events"""
        self.logger.info(
            f"Business event: {event_type}",
            extra={'extra_fields': {'business_event': {'type': event_type, **data}}}
        )


def get_request_id():
    """Generate or retrieve request ID"""
    if has_request_context():
        if not hasattr(g, 'request_id'):
            # Try to get from header or generate new one
            g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        return g.request_id
    return 'no-request-context'