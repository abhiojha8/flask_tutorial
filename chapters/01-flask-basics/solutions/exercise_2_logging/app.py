"""
Flask API with JSON-formatted structured logging
Demonstrates comprehensive logging with request tracking
"""

from flask import Flask, jsonify, request, g
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
import time
import random
from logger import setup_logging, APILogger, get_request_id
from middleware import LoggingMiddleware, PerformanceMonitor, AuditLogger


def create_app():
    """Create Flask app with structured logging"""
    app = Flask(__name__)

    # Basic configuration
    app.config['DEBUG'] = True
    app.config['LOG_LEVEL'] = 'DEBUG'
    app.config['ENV'] = 'development'

    # Set up JSON logging
    logger = setup_logging(app)

    # Initialize middleware
    LoggingMiddleware(app)
    perf_monitor = PerformanceMonitor(app)
    audit_logger = AuditLogger(app)
    api_logger = APILogger(logger)

    # Enable CORS
    CORS(app)

    # Initialize Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Logging Demo API',
        description='API demonstrating structured JSON logging',
        doc='/swagger',
        prefix='/api/v1'
    )

    # Create namespaces
    demo_ns = Namespace('demo', description='Demo operations')
    metrics_ns = Namespace('metrics', description='Metrics and monitoring')

    # Define models
    task_model = api.model('Task', {
        'id': fields.Integer(readonly=True),
        'title': fields.String(required=True),
        'completed': fields.Boolean()
    })

    # Sample data
    tasks = []

    @demo_ns.route('/tasks')
    class TaskList(Resource):
        @demo_ns.doc('list_tasks')
        @demo_ns.marshal_list_with(task_model)
        def get(self):
            """List all tasks with logging"""
            # Log API call
            api_logger.log_api_call('/tasks', 'GET', count=len(tasks))

            # Simulate database query
            query_time = random.uniform(10, 100)
            time.sleep(query_time / 1000)  # Convert to seconds
            api_logger.log_database_query("SELECT * FROM tasks", query_time)
            perf_monitor.record_metric('db_query', query_time)

            # Simulate cache check
            cache_hit = random.choice([True, False])
            api_logger.log_cache_hit('tasks:all', cache_hit)

            if not cache_hit:
                # Simulate loading from database
                time.sleep(0.05)

            return tasks

        @demo_ns.doc('create_task')
        @demo_ns.expect(task_model)
        @demo_ns.marshal_with(task_model, code=201)
        def post(self):
            """Create a task with audit logging"""
            new_task = {
                'id': len(tasks) + 1,
                'title': api.payload.get('title'),
                'completed': api.payload.get('completed', False)
            }
            tasks.append(new_task)

            # Log business event
            api_logger.log_business_event(
                'task_created',
                task_id=new_task['id'],
                title=new_task['title']
            )

            # Audit log
            audit_logger.log_data_access(
                user_id='demo-user',
                entity_type='task',
                entity_id=new_task['id'],
                action='create'
            )

            return new_task, 201

    @demo_ns.route('/slow')
    class SlowEndpoint(Resource):
        @demo_ns.doc('slow_operation')
        def get(self):
            """Simulate a slow operation"""
            logger.info("Starting slow operation")

            # Simulate slow processing
            delay = random.uniform(1.5, 3.0)
            time.sleep(delay)

            logger.info(f"Slow operation completed after {delay:.2f} seconds")

            return {'message': 'Slow operation completed', 'delay_seconds': delay}

    @demo_ns.route('/error')
    class ErrorEndpoint(Resource):
        @demo_ns.doc('trigger_error')
        def get(self):
            """Trigger an error for logging demonstration"""
            logger.warning("About to trigger an intentional error")

            try:
                # Simulate an error
                result = 1 / 0
            except Exception as e:
                logger.error(
                    "Intentional error triggered",
                    exc_info=True,
                    extra={'extra_fields': {'error_demo': True}}
                )
                raise

    @demo_ns.route('/external')
    class ExternalAPIEndpoint(Resource):
        @demo_ns.doc('external_api_call')
        def get(self):
            """Simulate external API call"""
            service = 'payment-gateway'
            endpoint = '/api/process'

            # Simulate external API call
            start_time = time.time()
            time.sleep(random.uniform(0.1, 0.5))
            duration_ms = (time.time() - start_time) * 1000
            status_code = random.choice([200, 200, 200, 500])

            api_logger.log_external_api_call(
                service=service,
                endpoint=endpoint,
                status_code=status_code,
                duration_ms=duration_ms
            )

            perf_monitor.record_metric('external_api', duration_ms)

            return {
                'service': service,
                'status': 'success' if status_code == 200 else 'failed',
                'duration_ms': duration_ms
            }

    @demo_ns.route('/auth')
    class AuthEndpoint(Resource):
        @demo_ns.doc('auth_demo')
        def post(self):
            """Simulate authentication for audit logging"""
            username = request.json.get('username', 'demo-user')
            success = random.choice([True, True, False])

            audit_logger.log_authentication(
                user_id=username,
                success=success,
                method='password'
            )

            if success:
                # Log authorization check
                audit_logger.log_authorization(
                    user_id=username,
                    resource='tasks',
                    action='read',
                    allowed=True
                )

                return {'status': 'authenticated', 'user': username}
            else:
                return {'status': 'authentication_failed'}, 401

    @metrics_ns.route('/logs/summary')
    class LogSummary(Resource):
        @metrics_ns.doc('log_summary')
        def get(self):
            """Get logging statistics"""
            return {
                'request_id': get_request_id(),
                'environment': app.config.get('ENV'),
                'log_level': app.config.get('LOG_LEVEL'),
                'handlers': len(logger.handlers)
            }

    @metrics_ns.route('/performance')
    class PerformanceMetrics(Resource):
        @metrics_ns.doc('performance_metrics')
        def get(self):
            """Get performance metrics"""
            perf_monitor.log_summary()

            metrics = {}
            for metric_name in ['db_query', 'external_api', 'cache_operation']:
                stats = perf_monitor.get_stats(metric_name)
                if stats:
                    metrics[metric_name] = stats

            return metrics

    # Register namespaces
    api.add_namespace(demo_ns)
    api.add_namespace(metrics_ns)

    # Log application startup
    logger.info(
        "Application initialized",
        extra={
            'extra_fields': {
                'startup': {
                    'environment': app.config.get('ENV'),
                    'debug': app.config.get('DEBUG'),
                    'namespaces': len(api.namespaces)
                }
            }
        }
    )

    return app


if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask application with structured logging")
    app.logger.info("Swagger UI available at: http://localhost:5000/swagger")
    app.run(host='0.0.0.0', port=5000, debug=True)