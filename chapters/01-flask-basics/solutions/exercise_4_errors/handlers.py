"""Global error handlers for Flask API.

This module provides comprehensive global error handling for Flask applications,
ensuring consistent error responses across all endpoints. Handles both custom
API exceptions and standard Python/Flask exceptions.

Features:
    - Consistent JSON error response format
    - Request ID tracking for debugging
    - Appropriate HTTP status codes
    - Detailed error logging
    - Security-conscious error messages (no stack traces in production)
    - Special handling for validation, HTTP, and Python exceptions

Error Response Format:
    All errors return JSON in this format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "details": {...},
            "request_id": "uuid",
            "timestamp": "2024-01-01T12:00:00Z",
            "path": "/api/endpoint",
            "method": "GET"
        }
    }

Example:
    Register error handlers in your app:
        >>> from handlers import register_error_handlers
        >>> app = Flask(__name__)
        >>> register_error_handlers(app)

    Errors are now automatically formatted:
        >>> raise NotFoundError(resource='User', resource_id=123)
        # Returns: {"error": {"code": "NOT_FOUND", ...}}
"""

import logging
from flask import g, jsonify, request
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError as MarshmallowValidationError
from exceptions import APIException
from datetime import datetime


logger = logging.getLogger(__name__)


def get_request_id():
    """Get request ID from Flask's g object.

    Returns:
        str: The request ID for the current request, or 'no-request-id' if not set.
    """
    return g.get('request_id', 'no-request-id')


def register_error_handlers(app):
    """Register all global error handlers with Flask application.

    Registers handlers for:
        - Custom API exceptions (APIException and subclasses)
        - Marshmallow validation errors
        - Werkzeug HTTP exceptions
        - Python built-in exceptions (ValueError, KeyError, TypeError)
        - Generic catch-all for unexpected errors

    Args:
        app (Flask): The Flask application instance.

    Implementation Notes:
        - Handlers are registered in order of specificity
        - Each handler logs the error with appropriate log level
        - Production mode hides internal error details
        - Request ID is included in all error responses
    """

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """Handle custom API exceptions.

        Args:
            error (APIException): The API exception that was raised.

        Returns:
            tuple: (JSON response, HTTP status code)

        Logs:
            ERROR level with exception details and request context
        """
        logger.error(
            f"API Exception: {error.code} - {error.message}",
            extra={
                'error_code': error.code,
                'status_code': error.status_code,
                'details': error.details,
                'request_id': get_request_id()
            }
        )

        response = error.to_dict(request_id=get_request_id())
        response['error']['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        response['error']['path'] = request.path
        response['error']['method'] = request.method

        return jsonify(response), error.status_code

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation_error(error):
        """Handle Marshmallow validation errors.

        Converts Marshmallow validation errors to standard API error format.

        Args:
            error (MarshmallowValidationError): Marshmallow validation exception.

        Returns:
            tuple: (JSON response, 400 status code)

        Logs:
            WARNING level with validation error details
        """
        logger.warning(
            "Validation error",
            extra={
                'errors': error.messages,
                'request_id': get_request_id()
            }
        )

        response = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Validation failed',
                'details': {
                    'errors': error.messages,
                    'fields': list(error.messages.keys())
                },
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path,
                'method': request.method
            }
        }

        return jsonify(response), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle Werkzeug HTTP exceptions.

        Handles standard HTTP exceptions like 404, 405, 413, etc. raised by
        Flask/Werkzeug when no custom exception is thrown.

        Args:
            error (HTTPException): Werkzeug HTTP exception.

        Returns:
            tuple: (JSON response, original HTTP status code)

        Logs:
            ERROR level with status code and request context
        """
        logger.error(
            f"HTTP Exception: {error.code} - {error.description}",
            extra={
                'status_code': error.code,
                'request_id': get_request_id()
            }
        )

        # Map HTTP status codes to error codes
        error_codes = {
            400: 'BAD_REQUEST',
            401: 'UNAUTHORIZED',
            403: 'FORBIDDEN',
            404: 'NOT_FOUND',
            405: 'METHOD_NOT_ALLOWED',
            408: 'REQUEST_TIMEOUT',
            409: 'CONFLICT',
            413: 'PAYLOAD_TOO_LARGE',
            415: 'UNSUPPORTED_MEDIA_TYPE',
            422: 'UNPROCESSABLE_ENTITY',
            429: 'TOO_MANY_REQUESTS',
            500: 'INTERNAL_SERVER_ERROR',
            501: 'NOT_IMPLEMENTED',
            502: 'BAD_GATEWAY',
            503: 'SERVICE_UNAVAILABLE',
            504: 'GATEWAY_TIMEOUT'
        }

        response = {
            'error': {
                'code': error_codes.get(error.code, 'UNKNOWN_ERROR'),
                'message': error.description or 'An error occurred',
                'details': {},
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path,
                'method': request.method
            }
        }

        return jsonify(response), error.code

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle Python ValueError exceptions.

        Catches ValueErrors (e.g., invalid type conversions) and converts
        them to API error responses.

        Args:
            error (ValueError): The ValueError that was raised.

        Returns:
            tuple: (JSON response, 400 status code)

        Logs:
            ERROR level with full stack trace
        """
        logger.error(
            f"Value error: {str(error)}",
            exc_info=True,
            extra={'request_id': get_request_id()}
        )

        response = {
            'error': {
                'code': 'INVALID_VALUE',
                'message': str(error),
                'details': {},
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path,
                'method': request.method
            }
        }

        return jsonify(response), 400

    @app.errorhandler(KeyError)
    def handle_key_error(error):
        """Handle Python KeyError exceptions.

        Catches KeyErrors (accessing missing dictionary keys) and converts
        them to API error responses.

        Args:
            error (KeyError): The KeyError that was raised.

        Returns:
            tuple: (JSON response, 400 status code)

        Logs:
            ERROR level with full stack trace
        """
        logger.error(
            f"Key error: {str(error)}",
            exc_info=True,
            extra={'request_id': get_request_id()}
        )

        response = {
            'error': {
                'code': 'MISSING_KEY',
                'message': f"Required key missing: {str(error)}",
                'details': {
                    'missing_key': str(error).strip("'")
                },
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path,
                'method': request.method
            }
        }

        return jsonify(response), 400

    @app.errorhandler(TypeError)
    def handle_type_error(error):
        """Handle Python TypeError exceptions.

        Catches TypeErrors (e.g., calling function with wrong types) and
        converts them to API error responses.

        Args:
            error (TypeError): The TypeError that was raised.

        Returns:
            tuple: (JSON response, 400 status code)

        Logs:
            ERROR level with full stack trace
        """
        logger.error(
            f"Type error: {str(error)}",
            exc_info=True,
            extra={'request_id': get_request_id()}
        )

        response = {
            'error': {
                'code': 'TYPE_ERROR',
                'message': 'Invalid type provided',
                'details': {
                    'error': str(error)
                },
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path,
                'method': request.method
            }
        }

        return jsonify(response), 400

    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 Not Found errors.

        Catches requests to non-existent endpoints.

        Args:
            error: The 404 error object.

        Returns:
            tuple: (JSON response, 404 status code)

        Logs:
            WARNING level (404s are common and not critical)
        """
        logger.warning(
            f"404 Not Found: {request.path}",
            extra={'request_id': get_request_id()}
        )

        response = {
            'error': {
                'code': 'NOT_FOUND',
                'message': f"The requested URL {request.path} was not found",
                'details': {
                    'path': request.path,
                    'method': request.method
                },
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }

        return jsonify(response), 404

    @app.errorhandler(405)
    def handle_405(error):
        """Handle 405 Method Not Allowed errors.

        Catches requests using unsupported HTTP methods.

        Args:
            error: The 405 error object.

        Returns:
            tuple: (JSON response, 405 status code)

        Logs:
            WARNING level
        """
        logger.warning(
            f"405 Method Not Allowed: {request.method} {request.path}",
            extra={'request_id': get_request_id()}
        )

        response = {
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': f"Method {request.method} is not allowed for {request.path}",
                'details': {
                    'method': request.method,
                    'path': request.path
                },
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }

        return jsonify(response), 405

    @app.errorhandler(500)
    def handle_500(error):
        """Handle 500 Internal Server Error.

        Catches unhandled server errors. In production, hides error details
        for security.

        Args:
            error: The 500 error object.

        Returns:
            tuple: (JSON response, 500 status code)

        Logs:
            ERROR level with full stack trace

        Security:
            - DEBUG mode: Full error message visible
            - Production: Generic error message only
        """
        logger.error(
            f"500 Internal Server Error: {str(error)}",
            exc_info=True,
            extra={'request_id': get_request_id()}
        )

        # Don't expose internal error details in production
        if app.config.get('DEBUG'):
            message = str(error)
        else:
            message = 'An internal server error occurred'

        response = {
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': message,
                'details': {},
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path,
                'method': request.method
            }
        }

        return jsonify(response), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle all unexpected exceptions (catch-all handler).

        This is the last resort handler for any exception not caught by
        more specific handlers.

        Args:
            error (Exception): Any Python exception.

        Returns:
            tuple: (JSON response, 500 status code)

        Logs:
            ERROR level with exception type and full stack trace

        Security:
            - DEBUG mode: Full error details including exception type
            - Production: Generic error message only
        """
        logger.error(
            f"Unexpected error: {str(error)}",
            exc_info=True,
            extra={
                'error_type': type(error).__name__,
                'request_id': get_request_id()
            }
        )

        # Don't expose internal error details in production
        if app.config.get('DEBUG'):
            message = str(error)
            details = {
                'type': type(error).__name__,
                'module': type(error).__module__
            }
        else:
            message = 'An unexpected error occurred'
            details = {}

        response = {
            'error': {
                'code': 'UNEXPECTED_ERROR',
                'message': message,
                'details': details,
                'request_id': get_request_id(),
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path,
                'method': request.method
            }
        }

        return jsonify(response), 500

    # Log that error handlers have been registered
    logger.info(f"Registered {len(app.error_handler_spec[None])} error handlers")