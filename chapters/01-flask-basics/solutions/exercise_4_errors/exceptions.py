"""Custom exception classes for Flask API.

This module provides a comprehensive hierarchy of custom exceptions for Flask
applications, enabling consistent error handling and meaningful error responses.
Each exception class includes appropriate HTTP status codes, error codes, and
structured error messages.

Exception Hierarchy:
    APIException (base)
    ├── ValidationError (400)
    ├── NotFoundError (404)
    ├── UnauthorizedError (401)
    ├── ForbiddenError (403)
    ├── ConflictError (409)
    ├── RateLimitError (429)
    ├── BusinessLogicError (400)
    ├── PayloadTooLargeError (413)
    ├── MethodNotAllowedError (405)
    ├── TimeoutError (408)
    ├── ExternalServiceError (503)
    ├── DatabaseError (500)
    └── MaintenanceError (503)

Benefits:
    - Consistent error response format across the API
    - Meaningful error codes for client error handling
    - Request ID tracking for debugging
    - Detailed error context for troubleshooting

Example:
    Raise an exception in your endpoint:
        >>> if not user:
        ...     raise NotFoundError(resource='User', resource_id=user_id)

    Handle with global error handler:
        >>> @app.errorhandler(APIException)
        ... def handle_api_exception(error):
        ...     return jsonify(error.to_dict()), error.status_code
"""

from werkzeug.exceptions import HTTPException


class APIException(Exception):
    """Base exception class for all API exceptions.

    All custom API exceptions should inherit from this class to ensure
    consistent error handling and response formatting.

    Attributes:
        status_code (int): HTTP status code for this error. Default: 500.
        code (str): Machine-readable error code. Default: "INTERNAL_ERROR".
        message (str): Human-readable error message.
        details (dict): Additional error context and details.

    Example:
        >>> raise APIException(
        ...     message="Something went wrong",
        ...     details={'operation': 'data_processing'}
        ... )
    """
    status_code = 500
    code = "INTERNAL_ERROR"
    message = "An internal error occurred"

    def __init__(self, message=None, code=None, status_code=None, details=None):
        """Initialize API exception with custom values.

        Args:
            message (str, optional): Override default error message.
            code (str, optional): Override default error code.
            status_code (int, optional): Override default HTTP status code.
            details (dict, optional): Additional error context.
        """
        super().__init__()
        if message:
            self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.details = details or {}

    def to_dict(self, request_id=None):
        """Convert exception to dictionary for JSON API response.

        Args:
            request_id (str, optional): Request ID for error tracking.

        Returns:
            dict: Structured error response with code, message, details, and request ID.

        Example:
            >>> error = NotFoundError(resource='User', resource_id=123)
            >>> error.to_dict(request_id='abc-123')
            {
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'User with id 123 not found',
                    'details': {'resource': 'User', 'resource_id': 123},
                    'request_id': 'abc-123'
                }
            }
        """
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
    """Validation error for invalid input data (HTTP 400).

    Raised when request data fails validation. Can include field-specific
    errors or general validation messages.

    Attributes:
        status_code: 400 (Bad Request)
        code: "VALIDATION_ERROR"

    Example:
        Single field error:
            >>> raise ValidationError(field='email', message='Invalid email format')

        Multiple field errors:
            >>> raise ValidationError(errors={
            ...     'email': 'Invalid format',
            ...     'age': 'Must be at least 18'
            ... })
    """
    status_code = 400
    code = "VALIDATION_ERROR"
    message = "Validation failed"

    def __init__(self, field=None, message=None, errors=None):
        """Initialize validation error.

        Args:
            field (str, optional): The specific field that failed validation.
            message (str, optional): Custom validation error message.
            errors (dict, optional): Dictionary of field names to error messages.
        """
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
    """Resource not found error (HTTP 404).

    Raised when a requested resource does not exist in the system.

    Attributes:
        status_code: 404 (Not Found)
        code: "NOT_FOUND"

    Example:
        >>> raise NotFoundError(resource='User', resource_id=123)
        # Message: "User with id 123 not found"

        >>> raise NotFoundError(resource='Product')
        # Message: "Product not found"
    """
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found"

    def __init__(self, resource=None, resource_id=None):
        """Initialize not found error.

        Args:
            resource (str, optional): The type of resource not found.
            resource_id: The identifier of the resource not found.
        """
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
    """Unauthorized access error (HTTP 401).

    Raised when authentication is required but not provided or invalid.
    Clients should provide valid credentials and retry.

    Attributes:
        status_code: 401 (Unauthorized)
        code: "UNAUTHORIZED"

    Example:
        >>> raise UnauthorizedError(
        ...     message='Invalid API key',
        ...     auth_type='Bearer'
        ... )
    """
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Unauthorized access"

    def __init__(self, message=None, auth_type=None):
        """Initialize unauthorized error.

        Args:
            message (str, optional): Custom error message.
            auth_type (str, optional): Expected authentication type
                (e.g., 'Bearer', 'Basic', 'API-Key').
        """
        details = {}
        if auth_type:
            details['auth_type'] = auth_type

        super().__init__(
            message=message or self.message,
            details=details
        )


class ForbiddenError(APIException):
    """Forbidden access error (HTTP 403).

    Raised when authenticated user lacks permission for the requested operation.
    Unlike 401, the client is authenticated but not authorized.

    Attributes:
        status_code: 403 (Forbidden)
        code: "FORBIDDEN"

    Example:
        >>> raise ForbiddenError(resource='admin_panel', action='access')
        # Message: "Cannot access admin_panel"
    """
    status_code = 403
    code = "FORBIDDEN"
    message = "Access forbidden"

    def __init__(self, resource=None, action=None):
        """Initialize forbidden error.

        Args:
            resource (str, optional): The resource being accessed.
            action (str, optional): The action being attempted.
        """
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
    """Resource conflict error (HTTP 409).

    Raised when attempting to create a resource that conflicts with existing
    data, such as duplicate unique fields.

    Attributes:
        status_code: 409 (Conflict)
        code: "CONFLICT"

    Example:
        >>> raise ConflictError(resource='User', conflict_field='email')
        # Message: "User with this email already exists"
    """
    status_code = 409
    code = "CONFLICT"
    message = "Resource conflict"

    def __init__(self, resource=None, conflict_field=None):
        """Initialize conflict error.

        Args:
            resource (str, optional): The type of resource.
            conflict_field (str, optional): The field causing the conflict.
        """
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
    """Rate limit exceeded error (HTTP 429).

    Raised when client exceeds allowed request rate. Includes retry information.

    Attributes:
        status_code: 429 (Too Many Requests)
        code: "RATE_LIMIT_EXCEEDED"

    Example:
        >>> raise RateLimitError(
        ...     limit=100,
        ...     window='1 hour',
        ...     retry_after=3600
        ... )
    """
    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"
    message = "Rate limit exceeded"

    def __init__(self, limit=None, window=None, retry_after=None):
        """Initialize rate limit error.

        Args:
            limit (int, optional): The rate limit (requests allowed).
            window (str, optional): The time window (e.g., '1 hour', '1 minute').
            retry_after (int, optional): Seconds until client can retry.
        """
        details = {}
        if limit:
            details['limit'] = limit
        if window:
            details['window'] = window
        if retry_after:
            details['retry_after'] = retry_after

        super().__init__(details=details)


class ExternalServiceError(APIException):
    """External service error (HTTP 503).

    Raised when an external dependency or third-party service is unavailable.

    Attributes:
        status_code: 503 (Service Unavailable)
        code: "EXTERNAL_SERVICE_ERROR"

    Example:
        >>> try:
        ...     call_payment_gateway()
        ... except Exception as e:
        ...     raise ExternalServiceError(service='payment-gateway', error=e)
    """
    status_code = 503
    code = "EXTERNAL_SERVICE_ERROR"
    message = "External service unavailable"

    def __init__(self, service=None, error=None):
        """Initialize external service error.

        Args:
            service (str, optional): Name of the external service.
            error (Exception, optional): The original exception from the service call.
        """
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
    """Database operation error (HTTP 500).

    Raised when a database operation fails unexpectedly.

    Attributes:
        status_code: 500 (Internal Server Error)
        code: "DATABASE_ERROR"

    Example:
        >>> try:
        ...     db.session.commit()
        ... except SQLAlchemyError as e:
        ...     raise DatabaseError(operation='commit', error=e)
    """
    status_code = 500
    code = "DATABASE_ERROR"
    message = "Database operation failed"

    def __init__(self, operation=None, error=None):
        """Initialize database error.

        Args:
            operation (str, optional): The database operation that failed.
            error (Exception, optional): The original database exception.
        """
        details = {}
        if operation:
            details['operation'] = operation
        if error:
            details['original_error'] = str(error)

        super().__init__(details=details)


class BusinessLogicError(APIException):
    """Business logic violation error (HTTP 400).

    Raised when an operation violates business rules or domain logic.
    Different from validation errors as these are context-specific rules.

    Attributes:
        status_code: 400 (Bad Request)
        code: "BUSINESS_LOGIC_ERROR"

    Example:
        >>> if order.total < minimum_order:
        ...     raise BusinessLogicError(
        ...         rule='minimum_order',
        ...         message='Order total must be at least $10'
        ...     )
    """
    status_code = 400
    code = "BUSINESS_LOGIC_ERROR"
    message = "Business rule violation"

    def __init__(self, rule=None, message=None):
        """Initialize business logic error.

        Args:
            rule (str, optional): Identifier for the business rule violated.
            message (str, optional): Human-readable explanation of the violation.
        """
        details = {}
        if rule:
            details['rule'] = rule

        super().__init__(
            message=message or self.message,
            details=details
        )


class PayloadTooLargeError(APIException):
    """Payload too large error (HTTP 413).

    Raised when request body exceeds size limits.

    Attributes:
        status_code: 413 (Payload Too Large)
        code: "PAYLOAD_TOO_LARGE"

    Example:
        >>> raise PayloadTooLargeError(
        ...     max_size='10MB',
        ...     actual_size='15MB'
        ... )
    """
    status_code = 413
    code = "PAYLOAD_TOO_LARGE"
    message = "Request payload too large"

    def __init__(self, max_size=None, actual_size=None):
        """Initialize payload too large error.

        Args:
            max_size: Maximum allowed payload size.
            actual_size: Actual payload size received.
        """
        details = {}
        if max_size:
            details['max_size'] = max_size
        if actual_size:
            details['actual_size'] = actual_size

        super().__init__(details=details)


class MethodNotAllowedError(APIException):
    """Method not allowed error (HTTP 405).

    Raised when HTTP method is not supported for the endpoint.

    Attributes:
        status_code: 405 (Method Not Allowed)
        code: "METHOD_NOT_ALLOWED"

    Example:
        >>> raise MethodNotAllowedError(
        ...     method='DELETE',
        ...     allowed_methods=['GET', 'POST']
        ... )
    """
    status_code = 405
    code = "METHOD_NOT_ALLOWED"
    message = "Method not allowed"

    def __init__(self, method=None, allowed_methods=None):
        """Initialize method not allowed error.

        Args:
            method (str, optional): The HTTP method that was used.
            allowed_methods (list, optional): List of allowed HTTP methods.
        """
        details = {}
        if method:
            details['method'] = method
        if allowed_methods:
            details['allowed_methods'] = allowed_methods

        super().__init__(details=details)


class TimeoutError(APIException):
    """Request timeout error (HTTP 408).

    Raised when an operation exceeds its time limit.

    Attributes:
        status_code: 408 (Request Timeout)
        code: "TIMEOUT"

    Example:
        >>> raise TimeoutError(
        ...     operation='database_query',
        ...     timeout_seconds=30
        ... )
    """
    status_code = 408
    code = "TIMEOUT"
    message = "Request timeout"

    def __init__(self, operation=None, timeout_seconds=None):
        """Initialize timeout error.

        Args:
            operation (str, optional): The operation that timed out.
            timeout_seconds (int, optional): The timeout threshold in seconds.
        """
        details = {}
        if operation:
            details['operation'] = operation
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds

        super().__init__(details=details)


class MaintenanceError(APIException):
    """Service under maintenance error (HTTP 503).

    Raised during planned maintenance windows.

    Attributes:
        status_code: 503 (Service Unavailable)
        code: "MAINTENANCE"

    Example:
        >>> raise MaintenanceError(
        ...     estimated_time='2024-01-01T12:00:00Z'
        ... )
    """
    status_code = 503
    code = "MAINTENANCE"
    message = "Service under maintenance"

    def __init__(self, estimated_time=None):
        """Initialize maintenance error.

        Args:
            estimated_time (str, optional): ISO 8601 timestamp of expected completion.
        """
        details = {}
        if estimated_time:
            details['estimated_completion'] = estimated_time

        super().__init__(details=details)