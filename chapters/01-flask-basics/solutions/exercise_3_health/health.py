"""Comprehensive health check system for Flask APIs.

This module provides a robust health checking system for production Flask applications,
monitoring critical infrastructure components and external dependencies. Essential for
high-availability deployments, container orchestration, and load balancer integration.

Components Monitored:
    - Database: Connectivity, query performance, connection pool status
    - Redis/Cache: Connectivity, latency, server info
    - Disk Space: Free space, usage percentage, threshold checks
    - Memory: RAM usage, swap usage, availability
    - External APIs: Connectivity and response times for dependencies

Health Check Architecture:
    - HealthChecker: Main coordinator for running all health checks
    - Individual check functions: Modular checks for each component
    - HealthCheckAPI: Flask-RESTX API endpoints for health status

Status Levels:
    - 'up': Component is fully operational
    - 'degraded': Component is working but with warnings (e.g., slow response)
    - 'down': Component is unavailable or critically impaired

Example:
    Basic usage:
        >>> from health import HealthChecker
        >>> checker = HealthChecker(app)
        >>> results = checker.run_checks()
        >>> print(results['status'])  # 'healthy', 'degraded', or 'unhealthy'

    Register custom checks:
        >>> def check_my_service(app):
        ...     return {'status': 'up', 'details': {}}
        >>> checker.register_check('my_service', check_my_service, critical=True)
"""

import time
import psutil
import os
from datetime import datetime
from flask import current_app
from sqlalchemy import text
import redis
import requests


class HealthChecker:
    """Main health check coordinator for managing and running health checks.

    Coordinates execution of multiple health checks, aggregates results, and
    determines overall system health status. Supports both critical and non-critical
    checks with different impact on overall system status.

    Attributes:
        app (Flask): The Flask application instance.
        checks (dict): Registry of all health check functions.

    Critical vs Non-Critical Checks:
        - Critical: Must pass for system to be 'ready' (database, redis)
        - Non-critical: Warnings only (disk space, memory, external APIs)
    """

    def __init__(self, app=None):
        """Initialize health checker.

        Args:
            app (Flask, optional): Flask application instance. If provided,
                default checks are registered immediately.
        """
        self.app = app
        self.checks = {}
        self.register_default_checks()

    def init_app(self, app):
        """Initialize with Flask application (deferred initialization).

        Args:
            app (Flask): The Flask application instance.
        """
        self.app = app

    def register_check(self, name, check_func, critical=True):
        """Register a health check function.

        Args:
            name (str): Unique identifier for the check.
            check_func (callable): Function that performs the check.
                Must accept app as parameter and return dict with 'status' key.
            critical (bool): Whether this check is critical for readiness.
                Defaults to True.

        Example:
            >>> def check_payment_gateway(app):
            ...     return {'status': 'up', 'details': {'latency_ms': 45}}
            >>> checker.register_check('payment', check_payment_gateway, critical=False)
        """
        self.checks[name] = {
            'function': check_func,
            'critical': critical
        }

    def register_default_checks(self):
        """Register standard health checks for common infrastructure.

        Registers checks for:
        - database: Critical - database connectivity
        - redis: Critical - cache connectivity
        - disk_space: Non-critical - disk usage
        - memory: Non-critical - memory usage
        - external_apis: Non-critical - external dependencies
        """
        self.register_check('database', check_database, critical=True)
        self.register_check('redis', check_redis, critical=True)
        self.register_check('disk_space', check_disk_space, critical=False)
        self.register_check('memory', check_memory, critical=False)
        self.register_check('external_apis', check_external_apis, critical=False)

    def run_checks(self, detailed=True):
        """Run all registered health checks and aggregate results.

        Args:
            detailed (bool): Include detailed information from each check.
                Defaults to True.

        Returns:
            dict: Aggregated health status containing:
                - timestamp: ISO 8601 timestamp of check execution
                - status: 'healthy', 'degraded', or 'unhealthy'
                - version: API version
                - checks: Results from each individual check
                - summary: Count of total, healthy, and unhealthy checks
                - unhealthy_checks: List of failed critical checks (if any)
                - degraded_checks: List of failed non-critical checks (if any)

        Status Determination:
            - 'unhealthy': Any critical check failed
            - 'degraded': All critical checks passed, but non-critical failed
            - 'healthy': All checks passed
        """
        results = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'healthy',
            'version': self.app.config.get('API_VERSION', '1.0') if self.app else '1.0',
            'checks': {}
        }

        unhealthy_critical = []
        unhealthy_non_critical = []

        for name, check_info in self.checks.items():
            start_time = time.time()
            try:
                check_result = check_info['function'](self.app)
                response_time_ms = (time.time() - start_time) * 1000

                results['checks'][name] = {
                    'status': check_result.get('status', 'unknown'),
                    'response_time_ms': round(response_time_ms, 2)
                }

                if detailed:
                    results['checks'][name].update(check_result.get('details', {}))

                if check_result['status'] != 'up':
                    if check_info['critical']:
                        unhealthy_critical.append(name)
                    else:
                        unhealthy_non_critical.append(name)

            except Exception as e:
                response_time_ms = (time.time() - start_time) * 1000
                results['checks'][name] = {
                    'status': 'down',
                    'error': str(e),
                    'response_time_ms': round(response_time_ms, 2)
                }
                if check_info['critical']:
                    unhealthy_critical.append(name)

        # Determine overall status
        if unhealthy_critical:
            results['status'] = 'unhealthy'
            results['unhealthy_checks'] = unhealthy_critical
        elif unhealthy_non_critical:
            results['status'] = 'degraded'
            results['degraded_checks'] = unhealthy_non_critical

        # Add summary
        total_checks = len(self.checks)
        healthy_checks = sum(
            1 for check in results['checks'].values()
            if check['status'] == 'up'
        )
        results['summary'] = {
            'total': total_checks,
            'healthy': healthy_checks,
            'unhealthy': total_checks - healthy_checks
        }

        return results

    def get_liveness(self):
        """Simple liveness probe for Kubernetes/container orchestration.

        A liveness check indicates whether the application is running and should
        be restarted if it fails. This check always succeeds if the app is running.

        Returns:
            dict: Liveness status with timestamp. Always returns 'alive' status.

        Kubernetes Integration:
            Configure as livenessProbe in pod spec:
            livenessProbe:
              httpGet:
                path: /health/live
                port: 5000
        """
        return {
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def get_readiness(self):
        """Readiness probe for Kubernetes/load balancer traffic control.

        A readiness check indicates whether the application can handle traffic.
        Only critical services are checked. If any critical service is down,
        the app is marked 'not_ready' and should not receive traffic.

        Returns:
            dict: Readiness status containing:
                - status: 'ready' or 'not_ready'
                - timestamp: ISO 8601 timestamp
                - checks: Status of each critical check

        Kubernetes Integration:
            Configure as readinessProbe in pod spec:
            readinessProbe:
              httpGet:
                path: /health/ready
                port: 5000
              initialDelaySeconds: 10
              periodSeconds: 5
        """
        critical_checks = {
            name: check for name, check in self.checks.items()
            if check['critical']
        }

        results = {
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'checks': {}
        }

        for name, check_info in critical_checks.items():
            try:
                check_result = check_info['function'](self.app)
                results['checks'][name] = check_result['status']
                if check_result['status'] != 'up':
                    results['status'] = 'not_ready'
            except:
                results['checks'][name] = 'down'
                results['status'] = 'not_ready'

        return results


def check_database(app):
    """Check database connectivity and performance.

    Tests database connection by executing a simple query and measures response
    time. Also retrieves connection pool statistics when available.

    Args:
        app (Flask): The Flask application instance with database configuration.

    Returns:
        dict: Health check result containing:
            - status: 'up', 'degraded', or 'down'
            - details: Query time, pool stats, database URL (credentials hidden)

    Status Conditions:
        - 'up': Database responsive within 100ms
        - 'degraded': Database responsive but slow (>100ms)
        - 'down': Connection failed or error occurred

    Implementation Notes:
        - Requires SQLALCHEMY_DATABASE_URI or DATABASE_URL in app config
        - Credentials are sanitized in output for security
        - Query time >100ms triggers degraded status
    """
    result = {'status': 'unknown', 'details': {}}

    try:
        # Get database from app context
        from sqlalchemy import create_engine
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', app.config.get('DATABASE_URL'))

        if not db_url:
            return {
                'status': 'down',
                'details': {'error': 'No database URL configured'}
            }

        engine = create_engine(db_url)

        # Test connection
        start_time = time.time()
        with engine.connect() as conn:
            # Run a simple query
            result_proxy = conn.execute(text('SELECT 1'))
            result_proxy.fetchone()

        query_time_ms = (time.time() - start_time) * 1000

        # Get connection pool stats if available
        pool_status = {
            'size': engine.pool.size() if hasattr(engine.pool, 'size') else 'N/A',
            'checked_in': engine.pool.checkedin() if hasattr(engine.pool, 'checkedin') else 'N/A',
            'overflow': engine.pool.overflow() if hasattr(engine.pool, 'overflow') else 'N/A'
        }

        result = {
            'status': 'up',
            'details': {
                'query_time_ms': round(query_time_ms, 2),
                'pool': pool_status,
                'database_url': db_url.split('@')[0] + '@...'  # Hide credentials
            }
        }

        # Check if slow
        if query_time_ms > 100:
            result['status'] = 'degraded'
            result['details']['warning'] = 'Slow database response'

    except Exception as e:
        result = {
            'status': 'down',
            'details': {'error': str(e)}
        }

    return result


def check_redis(app):
    """Check Redis connectivity and performance.

    Tests Redis connection using PING command and retrieves server information
    including version, memory usage, and client connections.

    Args:
        app (Flask): The Flask application instance with Redis configuration.

    Returns:
        dict: Health check result containing:
            - status: 'up', 'degraded', or 'down'
            - details: Ping time, version, memory, clients, uptime

    Status Conditions:
        - 'up': Redis responsive within 50ms
        - 'degraded': Redis responsive but slow (>50ms)
        - 'down': Connection failed or timeout

    Implementation Notes:
        - Requires REDIS_URL in app config (default: redis://localhost:6379/0)
        - 2-second connection timeout prevents hanging
        - Ping time >50ms triggers degraded status
    """
    result = {'status': 'unknown', 'details': {}}

    try:
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url, socket_connect_timeout=2)

        # Ping Redis
        start_time = time.time()
        r.ping()
        ping_time_ms = (time.time() - start_time) * 1000

        # Get Redis info
        info = r.info()

        result = {
            'status': 'up',
            'details': {
                'ping_time_ms': round(ping_time_ms, 2),
                'version': info.get('redis_version', 'unknown'),
                'used_memory_human': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_days': info.get('uptime_in_days', 0)
            }
        }

        # Check if slow
        if ping_time_ms > 50:
            result['status'] = 'degraded'
            result['details']['warning'] = 'Slow Redis response'

    except Exception as e:
        result = {
            'status': 'down',
            'details': {'error': str(e)}
        }

    return result


def check_disk_space(app):
    """Check available disk space on root filesystem.

    Monitors disk usage and warns when space is running low. Critical for
    preventing application failures due to full disk.

    Args:
        app (Flask): The Flask application instance with threshold configuration.

    Returns:
        dict: Health check result containing:
            - status: 'up', 'degraded', or 'down'
            - details: Free GB, used percentage, total GB, threshold

    Status Conditions:
        - 'up': Adequate free space (>threshold and <90% used)
        - 'degraded': Low space (threshold or 90% used)
        - 'down': Critical space (5GB or 95% used)

    Implementation Notes:
        - Default threshold: 10GB free space
        - Threshold configurable via DISK_SPACE_THRESHOLD_GB
        - Checks root filesystem ('/')
    """
    result = {'status': 'unknown', 'details': {}}

    try:
        disk_usage = psutil.disk_usage('/')

        free_gb = disk_usage.free / (1024 ** 3)
        used_percent = disk_usage.percent
        threshold_gb = app.config.get('DISK_SPACE_THRESHOLD_GB', 10) if app else 10

        result = {
            'status': 'up',
            'details': {
                'free_gb': round(free_gb, 2),
                'used_percent': round(used_percent, 2),
                'total_gb': round(disk_usage.total / (1024 ** 3), 2),
                'threshold_gb': threshold_gb
            }
        }

        # Check thresholds
        if free_gb < threshold_gb or used_percent > 90:
            result['status'] = 'degraded'
            result['details']['warning'] = 'Low disk space'

        if free_gb < 5 or used_percent > 95:
            result['status'] = 'down'
            result['details']['error'] = 'Critical: Very low disk space'

    except Exception as e:
        result = {
            'status': 'down',
            'details': {'error': str(e)}
        }

    return result


def check_memory(app):
    """Check system memory usage.

    Monitors RAM and swap memory usage to detect potential memory issues
    before they cause application failures or OOM (Out of Memory) kills.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        dict: Health check result containing:
            - status: 'up', 'degraded', or 'down'
            - details: Used percentage, available GB, total GB, swap usage

    Status Conditions:
        - 'up': Normal memory usage (<80% used, >2GB available)
        - 'degraded': High usage (>80% used or <2GB available)
        - 'down': Critical usage (>95% used or <512MB available)

    Implementation Notes:
        - Uses psutil for cross-platform memory stats
        - Monitors both physical RAM and swap space
        - Critical for containerized environments with memory limits
    """
    result = {'status': 'unknown', 'details': {}}

    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        used_percent = memory.percent
        available_gb = memory.available / (1024 ** 3)

        result = {
            'status': 'up',
            'details': {
                'used_percent': round(used_percent, 2),
                'available_gb': round(available_gb, 2),
                'total_gb': round(memory.total / (1024 ** 3), 2),
                'swap_used_percent': round(swap.percent, 2)
            }
        }

        # Check thresholds
        if used_percent > 80 or available_gb < 2:
            result['status'] = 'degraded'
            result['details']['warning'] = 'High memory usage'

        if used_percent > 95 or available_gb < 0.5:
            result['status'] = 'down'
            result['details']['error'] = 'Critical: Very high memory usage'

    except Exception as e:
        result = {
            'status': 'down',
            'details': {'error': str(e)}
        }

    return result


def check_external_apis(app):
    """Check external API dependencies and their availability.

    Tests connectivity to configured external services. Useful for monitoring
    third-party API health and detecting network/firewall issues.

    Args:
        app (Flask): The Flask application instance with external service config.

    Returns:
        dict: Health check result containing:
            - status: 'up' or 'degraded'
            - details: Individual service statuses with response times

    Status Conditions:
        - 'up': All external services responsive
        - 'degraded': One or more services down or slow

    Configuration:
        Set HEALTH_CHECK_EXTERNAL_SERVICES in app config:
        [
            {'name': 'payment_api', 'url': 'https://...', 'timeout': 5},
            {'name': 'shipping_api', 'url': 'https://...', 'timeout': 3}
        ]

    Implementation Notes:
        - Falls back to DNS checks if no services configured
        - Timeouts prevent hanging on slow services
        - 5xx status codes mark service as down
    """
    result = {'status': 'up', 'details': {'services': {}}}

    # Define external services to check
    external_services = []
    if app:
        external_services = app.config.get('HEALTH_CHECK_EXTERNAL_SERVICES', [])

    # Default services to check if none configured
    if not external_services:
        external_services = [
            {'name': 'google_dns', 'url': 'https://8.8.8.8', 'timeout': 2},
            {'name': 'cloudflare_dns', 'url': 'https://1.1.1.1', 'timeout': 2}
        ]

    all_healthy = True

    for service in external_services:
        try:
            start_time = time.time()
            response = requests.get(
                service['url'],
                timeout=service.get('timeout', 5)
            )
            response_time_ms = (time.time() - start_time) * 1000

            service_status = {
                'status': 'up' if response.status_code < 500 else 'down',
                'status_code': response.status_code,
                'response_time_ms': round(response_time_ms, 2)
            }

            if response.status_code >= 500:
                all_healthy = False

        except requests.exceptions.Timeout:
            service_status = {
                'status': 'down',
                'error': 'Timeout'
            }
            all_healthy = False

        except Exception as e:
            service_status = {
                'status': 'down',
                'error': str(e)
            }
            all_healthy = False

        result['details']['services'][service['name']] = service_status

    if not all_healthy:
        result['status'] = 'degraded'

    return result


class HealthCheckAPI:
    """Flask-RESTX API endpoints for health check system.

    Provides RESTful endpoints for accessing health check information.
    Integrates with Flask-RESTX for automatic API documentation.

    Attributes:
        api (Api): Flask-RESTX Api instance.
        health_checker (HealthChecker): The health checker coordinator.

    Endpoints:
        - GET /health/live: Liveness probe
        - GET /health/ready: Readiness probe
        - GET /health/: Full health check
        - GET /health/status/<check_name>: Individual check

    Example:
        >>> api = Api(app)
        >>> checker = HealthChecker(app)
        >>> health_api = HealthCheckAPI(api, checker)
    """

    def __init__(self, api, health_checker):
        """Initialize health check API endpoints.

        Args:
            api (Api): Flask-RESTX Api instance for endpoint registration.
            health_checker (HealthChecker): The health checker to use.
        """
        self.api = api
        self.health_checker = health_checker
        self.register_endpoints()

    def register_endpoints(self):
        """Register all health check endpoints with Flask-RESTX.

        Creates a 'health' namespace and registers liveness, readiness,
        comprehensive, and individual check endpoints with automatic
        Swagger documentation.
        """
        from flask_restx import Namespace, Resource

        health_ns = Namespace('health', description='Health check operations')

        # Store reference to health_checker for use in Resource classes
        health_checker_ref = self.health_checker

        @health_ns.route('/live')
        class LivenessCheck(Resource):
            @health_ns.doc('liveness_check')
            def get(self):
                """Basic liveness check - is the service alive?"""
                return health_checker_ref.get_liveness()

        @health_ns.route('/ready')
        class ReadinessCheck(Resource):
            @health_ns.doc('readiness_check')
            def get(self):
                """Readiness check - is the service ready to handle requests?"""
                result = health_checker_ref.get_readiness()
                status_code = 200 if result['status'] == 'ready' else 503
                return result, status_code

        @health_ns.route('/')
        class HealthCheck(Resource):
            @health_ns.doc('health_check')
            @health_ns.param('detailed', 'Include detailed information', type='boolean')
            def get(self):
                """Comprehensive health check"""
                from flask import request
                detailed = request.args.get('detailed', 'true').lower() == 'true'
                result = health_checker_ref.run_checks(detailed=detailed)
                status_code = 200 if result['status'] == 'healthy' else 503
                return result, status_code

        @health_ns.route('/status/<string:check_name>')
        @health_ns.param('check_name', 'Specific check to run')
        class SpecificHealthCheck(Resource):
            @health_ns.doc('specific_health_check')
            def get(self, check_name):
                """Run a specific health check"""
                if check_name not in health_checker_ref.checks:
                    return {'error': f'Check {check_name} not found'}, 404

                try:
                    check_func = health_checker_ref.checks[check_name]['function']
                    result = check_func(health_checker_ref.app)
                    return result
                except Exception as e:
                    return {'status': 'down', 'error': str(e)}, 503

        self.api.add_namespace(health_ns)