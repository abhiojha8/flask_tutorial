"""Logging middleware for Flask applications.

This module provides middleware components that integrate with Flask's request/response
lifecycle to add comprehensive logging, performance monitoring, and audit capabilities.

Key Components:
    - LoggingMiddleware: Automatic request/response logging with timing
    - PerformanceMonitor: Metrics collection and threshold alerting
    - AuditLogger: Security and compliance audit logging

The middleware uses Flask's before_request, after_request, and teardown_request
hooks to seamlessly integrate logging throughout the request lifecycle.

Example:
    Initialize middleware in your Flask app:
        >>> from middleware import LoggingMiddleware, PerformanceMonitor
        >>> app = Flask(__name__)
        >>> LoggingMiddleware(app)
        >>> perf_monitor = PerformanceMonitor(app)
        >>> perf_monitor.record_metric('db_query', 45.2)
"""

import time
from flask import g, request
from logger import get_request_id, log_request, log_response, APILogger


class LoggingMiddleware:
    """Middleware to automatically log all HTTP requests and responses.

    Integrates with Flask's request/response lifecycle to provide comprehensive
    logging including request details, response status, timing information, and
    error handling.

    Features:
        - Automatic request ID generation and tracking
        - Request/response logging with full context
        - Request duration tracking
        - Slow request detection and warnings
        - Exception logging with context

    Attributes:
        app (Flask): The Flask application instance.
        api_logger (APILogger): Enhanced logger for API operations.

    Example:
        >>> app = Flask(__name__)
        >>> middleware = LoggingMiddleware(app)
    """

    def __init__(self, app=None):
        """Initialize logging middleware.

        Args:
            app (Flask, optional): Flask application to initialize with.
                If provided, init_app is called automatically.
        """
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask application.

        Registers before_request, after_request, and teardown_request handlers
        for comprehensive logging coverage.

        Args:
            app (Flask): The Flask application instance to attach to.
        """
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

        # Create API logger
        self.api_logger = APILogger(app.logger)

    def before_request(self):
        """Handle before_request hook to set up logging and tracking.

        Sets up request ID, start time, and logs incoming request details.

        Side Effects:
            - Sets g.request_id for request correlation
            - Sets g.start_time for duration calculation
            - Logs request details
        """
        # Set request ID
        g.request_id = get_request_id()
        g.start_time = time.time()

        # Log request
        if self.app:
            log_request(self.app.logger)

    def after_request(self, response):
        """Handle after_request hook to log response details.

        Calculates request duration and logs response information with
        appropriate log level based on status code. Detects and warns
        about slow requests. Also adds the request ID to response headers.

        Args:
            response (flask.Response): The response object being returned.

        Returns:
            flask.Response: The response object with added headers.

        Implementation Notes:
            - Requests taking >1000ms are logged as warnings
            - Log level varies based on status code (ERROR for 5xx, WARNING for 4xx)
            - Adds X-Request-ID header for request tracing
        """
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id

        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            if self.app:
                log_response(self.app.logger, response, duration_ms)

                # Log slow requests
                if duration_ms > 1000:  # More than 1 second
                    self.app.logger.warning(
                        f"Slow request detected: {request.method} {request.path}",
                        extra={
                            'extra_fields': {
                                'performance': {
                                    'duration_ms': duration_ms,
                                    'threshold_ms': 1000
                                }
                            }
                        }
                    )

        return response

    def teardown_request(self, exception=None):
        """Handle teardown_request hook to log exceptions.

        Called at the end of the request, even if an exception occurred.
        Logs any exceptions with full context for debugging.

        Args:
            exception (Exception, optional): The exception that occurred during
                request processing, if any.
        """
        if exception and self.app:
            self.app.logger.error(
                f"Request failed: {request.method} {request.path}",
                exc_info=exception,
                extra={
                    'extra_fields': {
                        'error': {
                            'type': type(exception).__name__,
                            'message': str(exception)
                        }
                    }
                }
            )


class PerformanceMonitor:
    """Monitor and log performance metrics for API operations.

    Collects performance data for various operations and provides alerting
    when metrics exceed configured thresholds. Useful for identifying
    performance bottlenecks and monitoring system health.

    Attributes:
        app (Flask): The Flask application instance.
        metrics (dict): Dictionary storing collected metrics by metric name.

    Example:
        >>> monitor = PerformanceMonitor(app)
        >>> monitor.record_metric('db_query', 45.2)
        >>> stats = monitor.get_stats('db_query')
        >>> print(stats['avg'])  # Average query time
    """

    def __init__(self, app):
        """Initialize performance monitor.

        Args:
            app (Flask): The Flask application instance.
        """
        self.app = app
        self.metrics = {}

    def record_metric(self, metric_name, value, unit='ms'):
        """Record a performance metric and check thresholds.

        Args:
            metric_name (str): Name of the metric (e.g., 'db_query', 'external_api').
            value (float): The metric value to record.
            unit (str): The unit of measurement. Defaults to 'ms' (milliseconds).

        Implementation Notes:
            - Metrics are stored with timestamp and request ID
            - Threshold violations trigger warning logs
            - Default thresholds: db_query=100ms, external_api=500ms, cache_operation=10ms
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append({
            'value': value,
            'unit': unit,
            'timestamp': time.time(),
            'request_id': get_request_id()
        })

        # Log if metric exceeds threshold
        thresholds = {
            'db_query': 100,  # 100ms
            'external_api': 500,  # 500ms
            'cache_operation': 10  # 10ms
        }

        if metric_name in thresholds and value > thresholds[metric_name]:
            self.app.logger.warning(
                f"Performance threshold exceeded for {metric_name}",
                extra={
                    'extra_fields': {
                        'performance_alert': {
                            'metric': metric_name,
                            'value': value,
                            'threshold': thresholds[metric_name],
                            'unit': unit
                        }
                    }
                }
            )

    def get_stats(self, metric_name):
        """Get statistical summary for a specific metric.

        Args:
            metric_name (str): The name of the metric to get stats for.

        Returns:
            dict or None: Dictionary containing count, min, max, avg, and last_10
                values, or None if no data exists for the metric.

        Example:
            >>> stats = monitor.get_stats('db_query')
            >>> {
            ...     'count': 100,
            ...     'min': 5.2,
            ...     'max': 234.5,
            ...     'avg': 45.3,
            ...     'last_10': [42.1, 43.2, ...]
            ... }
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return None

        values = [m['value'] for m in self.metrics[metric_name]]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'last_10': values[-10:]
        }

    def log_summary(self):
        """Log a summary of all collected performance metrics.

        Aggregates and logs statistics for all tracked metrics. Useful for
        periodic reporting or debugging performance issues.
        """
        summary = {}
        for metric_name in self.metrics:
            stats = self.get_stats(metric_name)
            if stats:
                summary[metric_name] = stats

        if summary:
            self.app.logger.info(
                "Performance metrics summary",
                extra={'extra_fields': {'metrics_summary': summary}}
            )


class AuditLogger:
    """Specialized logger for security and compliance audit events.

    Provides methods for logging security-critical events such as authentication,
    authorization, data access, and configuration changes. These logs are essential
    for security monitoring, compliance, and forensic analysis.

    Attributes:
        app (Flask): The Flask application instance.

    Example:
        >>> audit_logger = AuditLogger(app)
        >>> audit_logger.log_authentication('user123', success=True, method='oauth')
        >>> audit_logger.log_data_access('user123', 'user', 456, 'update')
    """

    def __init__(self, app):
        """Initialize audit logger.

        Args:
            app (Flask): The Flask application instance.
        """
        self.app = app

    def log_authentication(self, user_id, success, method='password'):
        """Log authentication attempt for security audit.

        Args:
            user_id (str): The user identifier attempting authentication.
            success (bool): Whether the authentication succeeded.
            method (str): Authentication method used (e.g., 'password', 'oauth',
                'api_key'). Defaults to 'password'.

        Implementation Notes:
            - Includes IP address for security analysis
            - Critical for detecting brute force attacks
            - Required for many compliance frameworks
        """
        self.app.logger.info(
            f"Authentication {'succeeded' if success else 'failed'}",
            extra={
                'extra_fields': {
                    'audit': {
                        'type': 'authentication',
                        'user_id': user_id,
                        'success': success,
                        'method': method,
                        'ip_address': request.remote_addr if has_request_context() else None
                    }
                }
            }
        )

    def log_authorization(self, user_id, resource, action, allowed):
        """Log authorization decision for access control audit.

        Args:
            user_id (str): The user identifier requesting access.
            resource (str): The resource being accessed (e.g., 'tasks', 'admin_panel').
            action (str): The action being attempted (e.g., 'read', 'write', 'delete').
            allowed (bool): Whether access was granted.

        Implementation Notes:
            - Logs both allowed and denied access attempts
            - Essential for security incident investigation
            - Helps identify privilege escalation attempts
        """
        self.app.logger.info(
            f"Authorization {'granted' if allowed else 'denied'}",
            extra={
                'extra_fields': {
                    'audit': {
                        'type': 'authorization',
                        'user_id': user_id,
                        'resource': resource,
                        'action': action,
                        'allowed': allowed
                    }
                }
            }
        )

    def log_data_access(self, user_id, entity_type, entity_id, action):
        """Log data access for compliance and audit trail.

        Args:
            user_id (str): The user accessing the data.
            entity_type (str): Type of entity accessed (e.g., 'user', 'order', 'payment').
            entity_id: The specific entity identifier.
            action (str): The action performed (e.g., 'create', 'read', 'update', 'delete').

        Implementation Notes:
            - Required for GDPR, HIPAA, and other compliance frameworks
            - Creates audit trail for sensitive data access
            - Helps track who accessed what data and when
        """
        self.app.logger.info(
            f"Data access: {action} on {entity_type}",
            extra={
                'extra_fields': {
                    'audit': {
                        'type': 'data_access',
                        'user_id': user_id,
                        'entity_type': entity_type,
                        'entity_id': entity_id,
                        'action': action
                    }
                }
            }
        )

    def log_configuration_change(self, user_id, setting, old_value, new_value):
        """Log system configuration changes for audit and rollback.

        Args:
            user_id (str): The user making the configuration change.
            setting (str): The configuration setting being changed.
            old_value: The previous value of the setting.
            new_value: The new value of the setting.

        Implementation Notes:
            - Logged at WARNING level for visibility
            - Includes both old and new values for rollback capability
            - Essential for change management and incident response
            - Values are converted to strings for consistent logging
        """
        self.app.logger.warning(
            f"Configuration changed: {setting}",
            extra={
                'extra_fields': {
                    'audit': {
                        'type': 'config_change',
                        'user_id': user_id,
                        'setting': setting,
                        'old_value': str(old_value),
                        'new_value': str(new_value)
                    }
                }
            }
        )