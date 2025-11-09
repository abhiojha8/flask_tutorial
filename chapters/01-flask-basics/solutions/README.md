# Chapter 1: Exercise Solutions

Complete solutions for all Chapter 1 exercises demonstrating Flask API best practices.

## Solutions Overview

### ✅ Exercise 1: Environment Configuration
Multi-environment configuration system supporting development, testing, staging, and production.
- **Location**: `exercise_1_config/`
- **Key Files**: `config.py`, `app.py`, `.env.example`
- **Run**: `python exercise_1_config/app.py`

### ✅ Exercise 2: Structured Logging
JSON-formatted logging with request tracking and performance monitoring.
- **Location**: `exercise_2_logging/`
- **Key Files**: `logger.py`, `middleware.py`, `app.py`
- **Run**: `python exercise_2_logging/app.py`

### ✅ Exercise 3: Health Check System
Comprehensive health monitoring for database, Redis, disk, memory, and external services.
- **Location**: `exercise_3_health/`
- **Key Files**: `health.py`, `app.py`
- **Run**: `python exercise_3_health/app.py`

### ✅ Exercise 4: Error Handling
Custom exception hierarchy with consistent error responses.
- **Location**: `exercise_4_errors/`
- **Key Files**: `exceptions.py`, `handlers.py`, `app.py`
- **Run**: `python exercise_4_errors/app.py`

### ✅ Exercise 5: API Versioning
Support for multiple API versions with migration guides.
- **Location**: `exercise_5_versioning/`
- **Key Files**: `app.py`
- **Run**: `python exercise_5_versioning/app.py`

## Running the Solutions

### Prerequisites
```bash
pip install flask flask-restx flask-cors python-dotenv psutil redis requests
```

### Testing Each Solution

#### Exercise 1: Configuration
```bash
cd exercise_1_config
export FLASK_ENV=development  # or testing, staging, production
python app.py
# Visit http://localhost:5000/swagger
# Check /config/info and /config/environments endpoints
```

#### Exercise 2: Logging
```bash
cd exercise_2_logging
python app.py
# Visit http://localhost:5000/swagger
# Watch console for JSON-formatted logs
# Test various endpoints to see different log levels
```

#### Exercise 3: Health Checks
```bash
cd exercise_3_health
python app.py
# Visit http://localhost:5000/swagger
# Test health endpoints:
#   - /health/live (liveness)
#   - /health/ready (readiness)
#   - /health/ (comprehensive)
```

#### Exercise 4: Error Handling
```bash
cd exercise_4_errors
python app.py
# Visit http://localhost:5000/swagger
# Trigger various errors to see consistent responses
# Try: GET /api/v1/demo/users/999 for 404
```

#### Exercise 5: Versioning
```bash
cd exercise_5_versioning
python app.py
# Three Swagger UIs available:
#   - http://localhost:5000/api/v1/swagger (deprecated)
#   - http://localhost:5000/api/v2/swagger (current)
#   - http://localhost:5000/api/v3/swagger (beta)
# Check version info: http://localhost:5000/api/versions
```

## Key Learning Points

### From Exercise 1 (Configuration)
- Separate configuration classes for each environment
- Environment variable management with python-dotenv
- Configuration validation
- Feature flags implementation

### From Exercise 2 (Logging)
- JSON-formatted logs for better parsing
- Request ID tracking across logs
- Performance monitoring middleware
- Log rotation and multiple handlers

### From Exercise 3 (Health Checks)
- Liveness vs Readiness checks
- Component-level health monitoring
- Performance metrics in health responses
- Graceful degradation handling

### From Exercise 4 (Error Handling)
- Custom exception hierarchy
- Consistent error response format
- Global error handlers
- Request ID in error responses

### From Exercise 5 (Versioning)
- URL-based versioning (/api/v1/, /api/v2/)
- Header-based versioning (API-Version header)
- Deprecation warnings
- Migration guides between versions

## Testing with cURL

### Configuration Check
```bash
curl http://localhost:5000/api/v1/config/info
```

### Health Check
```bash
curl http://localhost:5000/api/v1/health/
```

### Trigger Error
```bash
curl http://localhost:5000/api/v1/demo/users/999
```

### Version Detection
```bash
# URL-based
curl http://localhost:5000/api/v2/tasks/

# Header-based
curl -H "API-Version: v3" http://localhost:5000/api/tasks/
```

## Production Considerations

1. **Configuration**: Store sensitive data in environment variables, never commit .env files
2. **Logging**: Use centralized log management (ELK stack, CloudWatch)
3. **Health Checks**: Integrate with container orchestration (Kubernetes probes)
4. **Error Handling**: Don't expose internal details in production
5. **Versioning**: Provide clear sunset dates and migration paths

## Next Steps

After mastering these concepts, proceed to:
- Chapter 2: RESTful API Design with Swagger
- Chapter 3: Database Design for APIs
- Chapter 4: API Authentication & Security