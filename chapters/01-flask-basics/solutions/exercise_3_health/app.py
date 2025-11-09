"""Flask API with comprehensive health check system.

This module demonstrates production-ready health monitoring for Flask applications,
implementing liveness, readiness, and comprehensive health checks. Essential for
containerized deployments, load balancers, and orchestration systems like Kubernetes.

Key Features:
    - Liveness checks: Is the application running?
    - Readiness checks: Can the application handle requests?
    - Comprehensive health checks: Detailed status of all dependencies
    - Database connectivity monitoring
    - Redis/cache health checks
    - Disk space and memory monitoring
    - External service dependency checks

Health Check Types:
    - /health/live: Basic liveness probe (is app alive?)
    - /health/ready: Readiness probe (is app ready for traffic?)
    - /health/: Full health check with all components
    - /health/status/<check_name>: Individual component check

Example:
    Run the application:
        $ python app.py

    Check application health:
        $ curl http://localhost:5000/health/
        $ curl http://localhost:5000/health/ready
        $ curl http://localhost:5000/health/status/database

Implementation Notes:
    - Critical checks (database, redis) affect readiness status
    - Non-critical checks (disk, memory) don't block traffic
    - Health checks return 503 when unhealthy for load balancer integration
    - Compatible with Kubernetes liveness and readiness probes
"""

from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from health import HealthChecker, HealthCheckAPI
import os


def create_app():
    """Create and configure Flask application with health monitoring.

    This factory function creates a Flask application with comprehensive health
    check capabilities for production deployments. Includes monitoring for
    databases, caches, system resources, and external dependencies.

    Returns:
        Flask: Configured Flask application with health check endpoints.

    Configuration:
        The app expects the following config values:
        - DATABASE_URL: Database connection string
        - REDIS_URL: Redis connection string
        - DISK_SPACE_THRESHOLD_GB: Minimum free disk space (GB)
        - HEALTH_CHECK_EXTERNAL_SERVICES: List of external services to monitor

    Health Check Endpoints:
        - GET /health/live: Liveness check (always returns 200 if app is running)
        - GET /health/ready: Readiness check (503 if critical services are down)
        - GET /health/: Comprehensive health status with details
        - GET /health/status/<check>: Individual health check status

    Example:
        >>> app = create_app()
        >>> app.run()
    """
    app = Flask(__name__)

    # Configuration
    app.config['DEBUG'] = True
    app.config['API_VERSION'] = '1.0'
    app.config['DATABASE_URL'] = 'sqlite:///health_demo.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['DISK_SPACE_THRESHOLD_GB'] = 10

    # External services to monitor
    app.config['HEALTH_CHECK_EXTERNAL_SERVICES'] = [
        {
            'name': 'github_api',
            'url': 'https://api.github.com/health',
            'timeout': 3
        },
        {
            'name': 'jsonplaceholder',
            'url': 'https://jsonplaceholder.typicode.com/health',
            'timeout': 3
        }
    ]

    # Enable CORS
    CORS(app)

    # Initialize Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Health Check Demo API',
        description='API with comprehensive health monitoring',
        doc='/swagger'
    )

    # Initialize health checker
    health_checker = HealthChecker(app)

    # Register custom health checks if needed
    def check_custom_service(app):
        """Custom health check example.

        Demonstrates how to add custom health checks for application-specific
        dependencies or business logic validation.

        Args:
            app (Flask): The Flask application instance.

        Returns:
            dict: Health check result with status and details.
                Must include 'status' key with value 'up', 'degraded', or 'down'.
        """
        # Implement your custom check logic
        return {
            'status': 'up',
            'details': {
                'custom_metric': 42,
                'custom_status': 'operational'
            }
        }

    health_checker.register_check('custom_service', check_custom_service, critical=False)

    # Register health check endpoints
    health_api = HealthCheckAPI(api, health_checker)

    return app


if __name__ == '__main__':
    app = create_app()

    print("\n" + "="*50)
    print("Health Check Demo API")
    print("="*50)
    print("Swagger UI: http://localhost:5000/swagger")
    print("\nHealth Check Endpoints:")
    print("  - Liveness:  http://localhost:5000/health/live")
    print("  - Readiness: http://localhost:5000/health/ready")
    print("  - Full:      http://localhost:5000/health/")
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)