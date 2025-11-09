"""
Multi-environment configuration system for Flask API
Supports development, testing, staging, and production environments
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration with common settings"""

    # Application settings
    APP_NAME = os.environ.get('APP_NAME', 'Flask Backend API')
    API_VERSION = os.environ.get('API_VERSION', '1.0')
    API_TITLE = os.environ.get('API_TITLE', 'Professional Flask API')
    API_DESCRIPTION = 'A production-ready Flask API with Swagger documentation'

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    DATABASE_QUERY_TIMEOUT = 300

    # API Settings
    RESTX_MASK_SWAGGER = False
    ERROR_404_HELP = False
    BUNDLE_ERRORS = True

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100 per hour"

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Feature flags
    FEATURE_REGISTRATION_ENABLED = True
    FEATURE_SOCIAL_AUTH = False
    FEATURE_TWO_FACTOR_AUTH = False

    # External services
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)

    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}

    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        # Base config has no specific validation
        # Override in subclasses for environment-specific validation
        return True


class DevelopmentConfig(Config):
    """Development environment configuration"""

    DEBUG = True
    TESTING = False
    ENV = 'development'

    # Database
    DATABASE_URL = os.environ.get(
        'DEV_DATABASE_URL',
        'sqlite:///dev.db'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_ECHO = True

    # Security (relaxed for development)
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

    # API Documentation
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True

    # Development features
    EXPLAIN_TEMPLATE_LOADING = True
    FEATURE_DEBUG_TOOLBAR = True

    # Hot reload
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class TestingConfig(Config):
    """Testing environment configuration"""

    DEBUG = False
    TESTING = True
    ENV = 'testing'

    # Database (in-memory for tests)
    DATABASE_URL = os.environ.get(
        'TEST_DATABASE_URL',
        'sqlite:///:memory:'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False

    # Test specific settings
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


class StagingConfig(Config):
    """Staging environment configuration"""

    DEBUG = False
    TESTING = False
    ENV = 'staging'

    # Database
    DATABASE_URL = os.environ.get(
        'STAGING_DATABASE_URL',
        'postgresql://user:pass@localhost/staging_db'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_ECHO = False

    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Performance
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_PRE_PING = True

    # Monitoring
    FEATURE_PERFORMANCE_MONITORING = True
    SENTRY_DSN = os.environ.get('SENTRY_DSN_STAGING')


class ProductionConfig(Config):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False
    ENV = 'production'

    # Database (required in production)
    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    # Handle Heroku-style postgres:// URLs
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///prod.db'
    SQLALCHEMY_ECHO = False

    # Security (strict in production)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Performance optimizations
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 seconds
        }
    }

    # Production logging
    LOG_LEVEL = 'WARNING'

    # Rate limiting (stricter in production)
    RATELIMIT_DEFAULT = "50 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')

    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    FEATURE_APM = True

    # SSL
    PREFERRED_URL_SCHEME = 'https'

    # Compression
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/javascript',
        'application/json', 'application/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

    @classmethod
    def validate(cls):
        """Validate production configuration"""
        warnings = []

        if not cls.DATABASE_URL:
            warnings.append("DATABASE_URL not set - using SQLite fallback")

        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("Using default SECRET_KEY - should be changed in production")

        if warnings:
            for warning in warnings:
                print(f"WARNING: {warning}")

        return True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration object based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    cfg = config.get(config_name, DevelopmentConfig)

    # Validate configuration
    cfg.validate()

    return cfg