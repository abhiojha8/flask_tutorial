"""
Flask API with Multi-Environment Configuration
Demonstrates proper configuration management for different environments
"""

from flask import Flask, jsonify
from flask_restx import Api, Resource, Namespace
from flask_cors import CORS
import logging
import sys
from config import get_config, config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory with environment-based configuration"""
    app = Flask(__name__)

    # Load configuration
    cfg = get_config(config_name)
    app.config.from_object(cfg)

    # Validate configuration
    logger.info(f"Loading configuration for environment: {cfg.ENV}")
    logger.info(f"Database URL: {cfg.DATABASE_URL[:20]}..." if cfg.DATABASE_URL else "No database configured")
    logger.info(f"Debug mode: {cfg.DEBUG}")
    logger.info(f"Testing mode: {cfg.TESTING}")

    # Enable CORS with configured origins
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Initialize Flask-RESTX
    api = Api(
        app,
        version=app.config['API_VERSION'],
        title=app.config['API_TITLE'],
        description=app.config['API_DESCRIPTION'],
        doc='/swagger',
        prefix='/api/v1'
    )

    # Create namespaces
    config_ns = Namespace('config', description='Configuration information')
    health_ns = Namespace('health', description='Health checks')

    @config_ns.route('/info')
    class ConfigInfo(Resource):
        @config_ns.doc('get_config_info')
        def get(self):
            """Get current configuration information (safe values only)"""
            return {
                'environment': app.config.get('ENV', 'unknown'),
                'app_name': app.config.get('APP_NAME'),
                'api_version': app.config.get('API_VERSION'),
                'debug': app.config.get('DEBUG'),
                'testing': app.config.get('TESTING'),
                'features': {
                    'registration': app.config.get('FEATURE_REGISTRATION_ENABLED'),
                    'social_auth': app.config.get('FEATURE_SOCIAL_AUTH'),
                    'two_factor_auth': app.config.get('FEATURE_TWO_FACTOR_AUTH'),
                },
                'limits': {
                    'page_size': app.config.get('DEFAULT_PAGE_SIZE'),
                    'max_page_size': app.config.get('MAX_PAGE_SIZE'),
                    'rate_limit': app.config.get('RATELIMIT_DEFAULT'),
                    'max_upload_size_mb': app.config.get('MAX_CONTENT_LENGTH', 0) / (1024 * 1024)
                }
            }

    @config_ns.route('/environments')
    class EnvironmentList(Resource):
        @config_ns.doc('list_environments')
        def get(self):
            """List available environments"""
            return {
                'current': app.config.get('ENV', 'unknown'),
                'available': list(config.keys())
            }

    @health_ns.route('/')
    class HealthCheck(Resource):
        @health_ns.doc('health_check')
        def get(self):
            """Basic health check"""
            return {
                'status': 'healthy',
                'environment': app.config.get('ENV'),
                'debug': app.config.get('DEBUG'),
                'app_name': app.config.get('APP_NAME')
            }

    @health_ns.route('/config')
    class ConfigHealth(Resource):
        @health_ns.doc('config_health_check')
        def get(self):
            """Check configuration health"""
            issues = []
            warnings = []

            # Check critical settings in production
            if app.config.get('ENV') == 'production':
                if app.config.get('DEBUG'):
                    issues.append("DEBUG is enabled in production!")
                if app.config.get('SECRET_KEY') == 'dev-secret-key-change-in-production':
                    issues.append("Using default SECRET_KEY in production!")
                if not app.config.get('DATABASE_URL'):
                    issues.append("No DATABASE_URL configured!")

            # Check recommended settings
            if not app.config.get('SENTRY_DSN') and app.config.get('ENV') in ['staging', 'production']:
                warnings.append("Sentry DSN not configured for error tracking")

            if app.config.get('ENV') == 'development' and not app.config.get('DEBUG'):
                warnings.append("DEBUG is disabled in development environment")

            return {
                'status': 'unhealthy' if issues else 'healthy',
                'issues': issues,
                'warnings': warnings,
                'environment': app.config.get('ENV'),
                'validated': True
            }

    # Register namespaces
    api.add_namespace(config_ns)
    api.add_namespace(health_ns)

    # Log configuration summary
    logger.info("=" * 50)
    logger.info(f"Application: {app.config.get('APP_NAME')}")
    logger.info(f"Environment: {app.config.get('ENV')}")
    logger.info(f"API Version: {app.config.get('API_VERSION')}")
    logger.info(f"Debug Mode: {app.config.get('DEBUG')}")
    logger.info(f"Swagger UI: http://localhost:5000/swagger")
    logger.info("=" * 50)

    return app


def run_app():
    """Run the application with environment detection"""
    import os

    # Detect environment from FLASK_ENV or default to development
    env = os.environ.get('FLASK_ENV', 'development')

    print(f"\nStarting application in {env.upper()} mode...")
    print(f"To change environment, set FLASK_ENV environment variable")
    print(f"Example: export FLASK_ENV=production\n")

    app = create_app(env)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False)
    )


if __name__ == '__main__':
    run_app()