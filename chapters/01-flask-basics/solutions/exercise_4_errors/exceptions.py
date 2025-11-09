"""
Custom exception classes for Flask API
Provides a hierarchy of exceptions with proper error codes and messages
"""

from werkzeug.exceptions import HTTPException


class APIException(Exception):
    """Base API exception class"""
    status_code = 500
    code = "INTERNAL_ERROR"
    message = "An internal error occurred"

    def __init__(self, message=None, code=None, status_code=None, details=None):
        super().__init__()
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.details = details or {}

    def to_dict(self, request_id=None):
        """Convert exception to dictionary for API response"""
        error_dict = {
            'error': {
                'code': self.code,
                'message': self.message,
                'details': self.details
            }
        }

        if request_id:
            error_dict['error']['request_id'] = request_id

        return error_dict


class ValidationError(APIException):
    """Validation error for invalid input data"""
    status_code = 400
    code = "VALIDATION_ERROR"
    message = "Validation failed"

    def __init__(self, field=None, message=None, errors=None):
        details = {}
        if field:
            details['field'] = field
        if errors:
            details['errors'] = errors

        super().__init__(
            message=message or self.message,
            details=details
        )


class NotFoundError(APIException):
    """Resource not found error"""
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"

    def __init__(self, resource=None, resource_id=None):
        details = {}
        if resource:
            details['resource'] = resource
        if resource_id:
            details['resource_id'] = resource_id

        message = self.message
        if resource and resource_id:
            message = f"{resource} with id {resource_id} not found"
        elif resource:
            message = f"{resource} not found"

        super().__init__(message=message, details=details)


class UnauthorizedError(APIException):
    """Unauthorized access error"""
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Unauthorized access"

    def __init__(self, message=None, auth_type=None):
        details = {}
        if auth_type:
            details['auth_type'] = auth_type

        super().__init__(
            message=message or self.message,
            details=details
        )


class ForbiddenError(APIException):
    """Forbidden access error"""
    status_code = 403
    code = "FORBIDDEN"
    message = "Access forbidden"

    def __init__(self, resource=None, action=None):
        details = {}
        if resource:
            details['resource'] = resource
        if action:
            details['action'] = action

        message = self.message
        if resource and action:
            message = f"Cannot {action} {resource}"

        super().__init__(message=message, details=details)


class ConflictError(APIException):
    """Resource conflict error"""
    status_code = 409
    code = "CONFLICT"
    message = "Resource conflict"

    def __init__(self, resource=None, conflict_field=None):
        details = {}
        if resource:
            details['resource'] = resource
        if conflict_field:
            details['conflict_field'] = conflict_field

        message = self.message
        if resource and conflict_field:
            message = f"{resource} with this {conflict_field} already exists"

        super().__init__(message=message, details=details)


class RateLimitError(APIException):
    """Rate limit exceeded error"""
    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"
    message = "Rate limit exceeded"

    def __init__(self, limit=None, window=None, retry_after=None):
        details = {}
        if limit:
            details['limit'] = limit
        if window:
            details['window'] = window
        if retry_after:
            details['retry_after'] = retry_after

        super().__init__(details=details)


class ExternalServiceError(APIException):
    """External service error"""
    status_code = 503
    code = "EXTERNAL_SERVICE_ERROR"
    message = "External service unavailable"

    def __init__(self, service=None, error=None):
        details = {}
        if service:
            details['service'] = service
        if error:
            details['original_error'] = str(error)

        message = self.message
        if service:
            message = f"External service '{service}' is unavailable"

        super().__init__(message=message, details=details)


class DatabaseError(APIException):
    """Database operation error"""
    status_code = 500
    code = "DATABASE_ERROR"
    message = "Database operation failed"

    def __init__(self, operation=None, error=None):
        details = {}
        if operation:
            details['operation'] = operation
        if error:
            details['original_error'] = str(error)

        super().__init__(details=details)


class BusinessLogicError(APIException):
    """Business logic violation error"""
    status_code = 400
    code = "BUSINESS_LOGIC_ERROR"
    message = "Business rule violation"

    def __init__(self, rule=None, message=None):
        details = {}
        if rule:
            details['rule'] = rule

        super().__init__(
            message=message or self.message,
            details=details
        )


class PayloadTooLargeError(APIException):
    """Payload too large error"""
    status_code = 413
    code = "PAYLOAD_TOO_LARGE"
    message = "Request payload too large"

    def __init__(self, max_size=None, actual_size=None):
        details = {}
        if max_size:
            details['max_size'] = max_size
        if actual_size:
            details['actual_size'] = actual_size

        super().__init__(details=details)


class MethodNotAllowedError(APIException):
    """Method not allowed error"""
    status_code = 405
    code = "METHOD_NOT_ALLOWED"
    message = "Method not allowed"

    def __init__(self, method=None, allowed_methods=None):
        details = {}
        if method:
            details['method'] = method
        if allowed_methods:
            details['allowed_methods'] = allowed_methods

        super().__init__(details=details)


class TimeoutError(APIException):
    """Request timeout error"""
    status_code = 408
    code = "TIMEOUT"
    message = "Request timeout"

    def __init__(self, operation=None, timeout_seconds=None):
        details = {}
        if operation:
            details['operation'] = operation
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds

        super().__init__(details=details)


class MaintenanceError(APIException):
    """Service under maintenance error"""
    status_code = 503
    code = "MAINTENANCE"
    message = "Service under maintenance"

    def __init__(self, estimated_time=None):
        details = {}
        if estimated_time:
            details['estimated_completion'] = estimated_time

        super().__init__(details=details)