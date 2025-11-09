# Chapter 1: Exercises

## 🎯 Exercise Overview

These exercises will help you master Flask API development with Swagger documentation. Each exercise builds on the concepts from the tutorial and demo application.

---

## Exercise 1: Environment Configuration (🟢 Basic)

### Objective
Create a robust configuration system that supports multiple environments with different settings.

### Requirements
1. Create a `config.py` file with classes for different environments
2. Support development, testing, staging, and production configurations
3. Load configuration from environment variables
4. Include database URLs, API keys, and feature flags
5. Implement configuration validation

### Expected Structure
```python
class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    API_TITLE = 'My API'
    API_VERSION = '1.0'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    DATABASE_URL = 'sqlite:///dev.db'

# Additional configurations...
```

### Success Criteria
- ✅ Four different environment configurations
- ✅ Environment variables properly loaded
- ✅ Sensitive data not hardcoded
- ✅ Configuration validation implemented
- ✅ Easy switching between environments

---

## Exercise 2: Structured Logging (🟢 Basic)

### Objective
Implement a comprehensive logging system with JSON formatting for better observability.

### Requirements
1. Create JSON-formatted logs
2. Add request ID to each log entry
3. Log API requests and responses
4. Implement different log levels
5. Add log rotation

### Expected Output
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "request_id": "abc-123-def",
  "method": "POST",
  "path": "/api/v1/tasks/",
  "status_code": 201,
  "duration_ms": 45,
  "message": "Task created successfully"
}
```

### Success Criteria
- ✅ JSON-formatted logs
- ✅ Request ID tracking
- ✅ Performance metrics logged
- ✅ Error details captured
- ✅ Log rotation configured

---

## Exercise 3: Health Check System (🟡 Intermediate)

### Objective
Build a comprehensive health check system that monitors various aspects of your API.

### Requirements
1. Create `/health/live` endpoint (basic liveness)
2. Create `/health/ready` endpoint (readiness check)
3. Check database connectivity
4. Check Redis connectivity
5. Check disk space and memory usage
6. Return detailed status for each component

### Expected Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "up",
      "response_time_ms": 5
    },
    "redis": {
      "status": "up",
      "response_time_ms": 2
    },
    "disk_space": {
      "status": "up",
      "free_gb": 45.2,
      "threshold_gb": 10
    },
    "memory": {
      "status": "up",
      "used_percent": 65
    }
  }
}
```

### Success Criteria
- ✅ Multiple health check endpoints
- ✅ Component-level health checks
- ✅ Performance metrics included
- ✅ Proper HTTP status codes
- ✅ Graceful handling of failures

---

## Exercise 4: Error Handling (🟡 Intermediate)

### Objective
Create a comprehensive error handling system with custom exceptions and proper HTTP responses.

### Requirements
1. Create custom exception classes
2. Implement global error handlers
3. Return consistent error format
4. Include error codes and messages
5. Log errors with stack traces
6. Handle validation errors specially

### Expected Error Response
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Task not found",
    "details": {
      "task_id": 123,
      "timestamp": "2024-01-15T10:30:45.123Z"
    },
    "request_id": "abc-123-def"
  }
}
```

### Custom Exceptions to Create
```python
class APIException(Exception):
    """Base API exception"""
    status_code = 500
    code = "INTERNAL_ERROR"

class NotFoundError(APIException):
    """Resource not found"""
    status_code = 404
    code = "NOT_FOUND"

class ValidationError(APIException):
    """Validation error"""
    status_code = 400
    code = "VALIDATION_ERROR"
```

### Success Criteria
- ✅ Custom exception hierarchy
- ✅ Global error handlers
- ✅ Consistent error format
- ✅ Proper status codes
- ✅ Error logging with context

---

## Exercise 5: API Versioning (🔴 Advanced)

### Objective
Implement a flexible API versioning system that supports multiple versions simultaneously.

### Requirements
1. Support URL-based versioning (`/api/v1/`, `/api/v2/`)
2. Support header-based versioning
3. Maintain backward compatibility
4. Version-specific documentation
5. Deprecation warnings for old versions
6. Version-specific business logic

### Implementation Approaches

#### URL-Based Versioning
```python
# /api/v1/tasks
v1 = Namespace('tasks', description='Task operations v1')

# /api/v2/tasks
v2 = Namespace('tasks', description='Task operations v2')
```

#### Header-Based Versioning
```python
# API-Version: 1.0
@app.before_request
def check_api_version():
    version = request.headers.get('API-Version', '1.0')
    g.api_version = version
```

### Expected Features
- Different response formats per version
- Version-specific field names
- Deprecated endpoint warnings
- Version sunset dates
- Migration guides in documentation

### Success Criteria
- ✅ Multiple API versions running
- ✅ Version detection implemented
- ✅ Backward compatibility maintained
- ✅ Version-specific documentation
- ✅ Deprecation warnings working
- ✅ Clean version isolation

---

## 📝 Submission Guidelines

### For Each Exercise:
1. Create a separate folder in `exercises/`
2. Include all source code
3. Add a README with your approach
4. Include test cases
5. Document any assumptions

### Folder Structure
```
exercises/
├── exercise_1_config/
│   ├── config.py
│   ├── app.py
│   └── README.md
├── exercise_2_logging/
│   ├── logger.py
│   ├── middleware.py
│   └── README.md
└── ...
```

---

## 🎓 Tips for Success

### General Tips
- Start with the basic exercises first
- Test your implementation thoroughly
- Use the demo application as reference
- Check Flask-RESTX documentation
- Write clean, documented code

### Testing Your Solutions
```bash
# Run your solution
python exercises/exercise_1_config/app.py

# Test with curl
curl http://localhost:5000/api/v1/health/

# Check Swagger UI
open http://localhost:5000/swagger
```

### Common Pitfalls to Avoid
- ❌ Hardcoding configuration values
- ❌ Ignoring error handling
- ❌ Missing input validation
- ❌ Poor logging practices
- ❌ Tight coupling between components

---

## 🏆 Bonus Challenges

### Challenge 1: Metrics Collection
Add Prometheus metrics collection to your API with custom metrics for request counts, latencies, and error rates.

### Challenge 2: Request Validation Middleware
Create middleware that validates all incoming requests against OpenAPI schemas automatically.

### Challenge 3: Rate Limiting
Implement rate limiting with different limits for different API endpoints and user tiers.

---

## 📚 Resources

- [Flask Configuration Handling](https://flask.palletsprojects.com/en/3.0.x/config/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Health Check RFC](https://tools.ietf.org/html/draft-inadarei-api-health-check-06)
- [REST API Error Handling](https://www.baeldung.com/rest-api-error-handling-best-practices)
- [API Versioning Strategies](https://www.xmatters.com/blog/api-versioning-strategies/)

---

**Ready to test your skills?** Start with Exercise 1 and work your way through. Solutions are available in the `solutions/` branch if you get stuck!