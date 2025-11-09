"""
Comprehensive health check system for Flask APIs
Monitors database, cache, disk, memory, and external services
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
    """Main health check coordinator"""

    def __init__(self, app=None):
        self.app = app
        self.checks = {}
        self.register_default_checks()

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app

    def register_check(self, name, check_func, critical=True):
        """Register a health check"""
        self.checks[name] = {
            'function': check_func,
            'critical': critical
        }

    def register_default_checks(self):
        """Register standard health checks"""
        self.register_check('database', check_database, critical=True)
        self.register_check('redis', check_redis, critical=True)
        self.register_check('disk_space', check_disk_space, critical=False)
        self.register_check('memory', check_memory, critical=False)
        self.register_check('external_apis', check_external_apis, critical=False)

    def run_checks(self, detailed=True):
        """Run all registered health checks"""
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
        """Simple liveness check"""
        return {
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def get_readiness(self):
        """Readiness check - only critical services"""
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
    """Check database connectivity and performance"""
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
    """Check Redis connectivity and performance"""
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
    """Check available disk space"""
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
    """Check memory usage"""
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
    """Check external API dependencies"""
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
    """Health check API endpoints"""

    def __init__(self, api, health_checker):
        self.api = api
        self.health_checker = health_checker
        self.register_endpoints()

    def register_endpoints(self):
        """Register health check endpoints"""
        from flask_restx import Namespace, Resource

        health_ns = Namespace('health', description='Health check operations')

        @health_ns.route('/live')
        class LivenessCheck(Resource):
            @health_ns.doc('liveness_check')
            def get(self):
                """Basic liveness check - is the service alive?"""
                return self.health_checker.get_liveness()

        @health_ns.route('/ready')
        class ReadinessCheck(Resource):
            @health_ns.doc('readiness_check')
            def get(self):
                """Readiness check - is the service ready to handle requests?"""
                result = self.health_checker.get_readiness()
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
                result = self.health_checker.run_checks(detailed=detailed)
                status_code = 200 if result['status'] == 'healthy' else 503
                return result, status_code

        @health_ns.route('/status/<string:check_name>')
        @health_ns.param('check_name', 'Specific check to run')
        class SpecificHealthCheck(Resource):
            @health_ns.doc('specific_health_check')
            def get(self, check_name):
                """Run a specific health check"""
                if check_name not in self.health_checker.checks:
                    return {'error': f'Check {check_name} not found'}, 404

                try:
                    check_func = self.health_checker.checks[check_name]['function']
                    result = check_func(self.health_checker.app)
                    return result
                except Exception as e:
                    return {'status': 'down', 'error': str(e)}, 503

        self.api.add_namespace(health_ns)