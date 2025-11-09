"""
Flask API with comprehensive health check system
Demonstrates production-ready health monitoring
"""

from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from health import HealthChecker, HealthCheckAPI
import os


def create_app():
    """Create Flask app with health checks"""
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
        """Custom health check example"""
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