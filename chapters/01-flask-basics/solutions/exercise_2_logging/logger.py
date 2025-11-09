"""JSON-formatted logging system with request tracking.

This module provides a comprehensive structured logging system for Flask applications
using JSON formatting for machine-readable logs. It implements request ID tracking,
custom formatters, and specialized loggers for different logging needs.

Key Components:
    - JSONFormatter: Converts log records to JSON format
    - RequestIdFilter: Adds request IDs to all log records
    - APILogger: Enhanced logger with methods for common API logging patterns
    - setup_logging: Main configuration function for application logging

Benefits of JSON Logging:
    - Machine-readable format for log aggregation tools
    - Easy parsing and querying in log management systems
    - Consistent structure across all log entries
    - Support for nested data structures
    - Better correlation of related log entries

Example:
    Configure logging in your Flask app:
        >>> from logger import setup_logging
        >>> app = Flask(__name__)
        >>> logger = setup_logging(app)
        >>> logger.info("Application started")

    Use the API logger for structured logging:
        >>> api_logger = APILogger(logger)
        >>> api_logger.log_database_query("SELECT * FROM users", 45.2)
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
    """Custom JSON formatter for structured logging.

    Converts Python logging records into JSON-formatted strings for better
    machine readability and integration with log aggregation systems.

    The formatter includes:
        - Timestamp in ISO 8601 format with UTC timezone
        - Log level and logger name
        - Message and source location (module, function, line)
        - Flask request context (if available)
        - Exception information with stack traces
        - Custom extra fields

    Attributes:
        Standard logging.Formatter attributes are inherited.
    """

    def format(self, record):
        """Format a log record as a JSON string.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: JSON-formatted log entry as a string.

        Implementation Notes:
            - Timestamps are in UTC with 'Z' suffix
            - Request context is automatically added when available
            - Exception stack traces are included when present
            - Extra fields from logger calls are merged into the output
        """
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
    """Logging filter that adds request ID to all log records.

    This filter ensures every log entry includes a request ID for distributed
    tracing and correlation of log entries across a request lifecycle.

    The request ID is retrieved from Flask's request context (g object) when
    available, otherwise a placeholder is used.
    """

    def filter(self, record):
        """Add request_id attribute to log record.

        Args:
            record (logging.LogRecord): The log record to modify.

        Returns:
            bool: Always returns True to allow the record to be logged.

        Implementation Notes:
            - Checks for Flask request context availability
            - Retrieves request ID from g.request_id if available
            - Falls back to 'no-request-id' if within a request but ID not set
            - Falls back to 'no-request-context' if outside request context
        """
        if has_request_context():
            record.request_id = g.get('request_id', 'no-request-id')
        else:
            record.request_id = 'no-request-context'
        return True


def setup_logging(app):
    """Configure JSON logging for the Flask application.

    Sets up comprehensive logging with JSON formatting, file rotation, and
    separate error logging. Creates multiple handlers for different log
    destinations and severity levels.

    Args:
        app (Flask): The Flask application instance to configure logging for.

    Returns:
        logging.Logger: The configured application logger.

    Logging Configuration:
        - Console handler: JSON-formatted logs to stdout
        - File handler: Rotating log files (10MB max, 10 backups)
        - Error handler: Separate file for ERROR and above
        - All handlers use JSONFormatter and RequestIdFilter

    Implementation Notes:
        - Creates logs/ directory if it doesn't exist
        - Log level is read from app.config['LOG_LEVEL'] (default: INFO)
        - File handlers are skipped in testing environment
        - All logs include request ID for correlation
        - Rotation prevents log files from growing too large
    """

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
    """Log incoming HTTP request details with full context.

    Logs comprehensive information about incoming requests including method,
    path, query parameters, headers, and client information.

    Args:
        logger (logging.Logger): The logger instance to use for logging.

    Implementation Notes:
        - Only logs when within a Flask request context
        - Captures full request headers for debugging
        - Records user agent string for client identification
        - Query parameters are logged for request reconstruction
        - Remote address logged for security audit trails
    """
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
    """Log HTTP response details with appropriate log level.

    Logs response information with log level based on HTTP status code:
    - ERROR (500+): Server errors
    - WARNING (400-499): Client errors
    - INFO (< 400): Successful responses

    Args:
        logger (logging.Logger): The logger instance to use.
        response (flask.Response): The Flask response object.
        duration_ms (float, optional): Request processing duration in milliseconds.

    Implementation Notes:
        - Status code determines log level automatically
        - Duration is included when provided
        - Content-Length and Content-Type logged for debugging
        - Only logs when within request context
    """
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
    """Enhanced logger for API endpoints with specialized logging methods.

    Provides high-level logging methods for common API operations including
    database queries, cache operations, external API calls, and business events.

    This logger wraps a standard Python logger and adds context-aware methods
    that structure log entries consistently.

    Attributes:
        logger (logging.Logger): The underlying logger instance.

    Example:
        >>> logger = logging.getLogger(__name__)
        >>> api_logger = APILogger(logger)
        >>> api_logger.log_database_query("SELECT * FROM users", 45.2)
        >>> api_logger.log_cache_hit("user:123", hit=True)
    """

    def __init__(self, logger):
        """Initialize APILogger with a standard logger.

        Args:
            logger (logging.Logger): The logger instance to wrap.
        """
        self.logger = logger

    def log_api_call(self, endpoint, method, **kwargs):
        """Log API endpoint call with additional context.

        Args:
            endpoint (str): The API endpoint path.
            method (str): The HTTP method (GET, POST, etc.).
            **kwargs: Additional context to include in the log (e.g., count, filters).

        Example:
            >>> api_logger.log_api_call('/users', 'GET', count=42, page=2)
        """
        self.logger.info(
            f"API call: {method} {endpoint}",
            extra={'extra_fields': {'api_call': kwargs}}
        )

    def log_database_query(self, query, duration_ms):
        """Log database query execution and performance.

        Args:
            query (str): The SQL query or description. Long queries are truncated
                to 500 characters.
            duration_ms (float): Query execution time in milliseconds.

        Implementation Notes:
            - Queries longer than 500 characters are truncated
            - Logged at DEBUG level for development debugging
            - Duration helps identify slow queries
        """
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
        """Log cache access result (hit or miss).

        Args:
            key (str): The cache key accessed.
            hit (bool): True if cache hit, False if cache miss. Defaults to True.

        Implementation Notes:
            - Useful for monitoring cache efficiency
            - Logged at DEBUG level
            - Can be aggregated to calculate cache hit ratio
        """
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
        """Log external API call details and performance.

        Args:
            service (str): Name of the external service (e.g., 'payment-gateway').
            endpoint (str): The endpoint path called.
            status_code (int): HTTP status code returned.
            duration_ms (float): Request duration in milliseconds.

        Implementation Notes:
            - Essential for monitoring external dependencies
            - Duration helps identify slow external services
            - Status codes help track service health
            - Logged at INFO level for visibility
        """
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
        """Log business-level events for analytics and monitoring.

        Business events represent important domain actions like order placement,
        user registration, payment processing, etc.

        Args:
            event_type (str): Type of business event (e.g., 'order_placed',
                'user_registered').
            **data: Additional event data as keyword arguments.

        Example:
            >>> api_logger.log_business_event(
            ...     'order_placed',
            ...     order_id=12345,
            ...     amount=99.99,
            ...     currency='USD'
            ... )
        """
        self.logger.info(
            f"Business event: {event_type}",
            extra={'extra_fields': {'business_event': {'type': event_type, **data}}}
        )


def get_request_id():
    """Generate or retrieve the current request ID.

    Returns:
        str: The request ID for the current request, or a placeholder if no
            request context exists.

    Implementation Notes:
        - First checks Flask's g object for existing request ID
        - Looks for X-Request-ID header if not in g
        - Generates new UUID if neither exists
        - Returns 'no-request-context' if outside request context
        - Request ID is stored in g to ensure consistency within a request
    """
    if has_request_context():
        if not hasattr(g, 'request_id'):
            # Try to get from header or generate new one
            g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        return g.request_id
    return 'no-request-context'