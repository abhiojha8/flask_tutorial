"""
Logging middleware for Flask applications
Adds request tracking and performance monitoring
"""

import time
from flask import g, request
from logger import get_request_id, log_request, log_response, APILogger


class LoggingMiddleware:
    """Middleware to log all requests and responses"""

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

        # Create API logger
        self.api_logger = APILogger(app.logger)

    def before_request(self):
        """Log request and set up tracking"""
        # Set request ID
        g.request_id = get_request_id()
        g.start_time = time.time()

        # Log request
        if self.app:
            log_request(self.app.logger)

            # Add request ID to response headers
            @self.app.after_request
            def add_request_id_header(response):
                response.headers['X-Request-ID'] = g.request_id
                return response

    def after_request(self, response):
        """Log response with timing"""
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
        """Clean up and log any exceptions"""
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
    """Monitor and log performance metrics"""

    def __init__(self, app):
        self.app = app
        self.metrics = {}

    def record_metric(self, metric_name, value, unit='ms'):
        """Record a performance metric"""
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
        """Get statistics for a metric"""
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
        """Log performance summary"""
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
    """Specialized logger for audit events"""

    def __init__(self, app):
        self.app = app

    def log_authentication(self, user_id, success, method='password'):
        """Log authentication attempts"""
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
        """Log authorization decisions"""
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
        """Log data access for compliance"""
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
        """Log configuration changes"""
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