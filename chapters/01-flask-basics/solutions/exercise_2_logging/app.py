"""Flask API with JSON-formatted structured logging.

This module demonstrates comprehensive structured logging in a Flask application using
JSON-formatted logs for better observability and monitoring. It showcases various logging
patterns including request tracking, performance monitoring, audit logging, and business
event logging.

Key Features:
    - JSON-formatted structured logging for machine-readable logs
    - Request ID tracking across the application lifecycle
    - Performance monitoring with custom metrics
    - Audit logging for security and compliance
    - Database query and external API call logging
    - Automatic slow request detection

The application uses Flask-RESTX for API documentation and implements multiple middleware
components for comprehensive logging coverage.

Example:
    Run the application:
        $ python app.py

    Access the API:
        $ curl http://localhost:5000/api/v1/demo/tasks

    View logs in logs/app.log with JSON-formatted entries
"""

from flask import Flask, jsonify, request, g
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
import time
import random
from logger import setup_logging, APILogger, get_request_id
from middleware import LoggingMiddleware, PerformanceMonitor, AuditLogger


def create_app():
    """Create and configure Flask application with structured logging.

    This factory function creates a Flask application instance with comprehensive
    logging configuration including JSON formatting, request tracking, performance
    monitoring, and audit logging capabilities.

    The function sets up:
        - JSON-formatted logging to both console and file
        - Request ID middleware for distributed tracing
        - Performance monitoring middleware
        - Audit logging middleware
        - Flask-RESTX API documentation
        - CORS support
        - Demo endpoints showcasing various logging patterns

    Returns:
        Flask: Configured Flask application instance with logging middleware
            and demo endpoints.

    Implementation Notes:
        - All logs are written in JSON format for better parsing and analysis
        - Request IDs are automatically generated and tracked
        - Performance metrics are collected for database queries and external APIs
        - Slow requests (>1s) are automatically logged as warnings
        - Audit logs capture authentication, authorization, and data access events
    """
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
            """List all tasks with comprehensive logging demonstration.

            This endpoint demonstrates various logging patterns including:
            - API call logging with context
            - Database query performance logging
            - Cache hit/miss logging
            - Simulated latency tracking

            Returns:
                list: List of task dictionaries with id, title, and completed fields.

            Logs Generated:
                - INFO: API call with task count
                - DEBUG: Database query execution with timing
                - DEBUG: Cache hit/miss status
            """
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
            """Create a task with audit logging demonstration.

            Demonstrates business event logging and audit logging patterns
            for tracking important operations and data access.

            Returns:
                tuple: (task dict, 201 status code) for the created task.

            Logs Generated:
                - INFO: Business event for task creation
                - INFO: Audit log for data access (create operation)
            """
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
            """Simulate a slow operation to demonstrate performance logging.

            This endpoint intentionally delays the response to trigger slow
            request warnings in the logging middleware. Useful for testing
            performance monitoring and alerting.

            Returns:
                dict: Message with the delay duration.

            Logs Generated:
                - INFO: Operation start
                - INFO: Operation completion with duration
                - WARNING: Slow request alert (automatically by middleware)
            """
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
            """Trigger an error for logging demonstration.

            Demonstrates error logging with full stack traces and contextual
            information. Shows how exceptions are captured and logged.

            Returns:
                Never returns - always raises an exception.

            Raises:
                ZeroDivisionError: Intentionally raised for demonstration.

            Logs Generated:
                - WARNING: Pre-error notification
                - ERROR: Exception with full stack trace
            """
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
            """Simulate external API call with performance tracking.

            Demonstrates logging of external service interactions including
            timing, status codes, and correlation for distributed tracing.

            Returns:
                dict: Service response details with timing information.

            Logs Generated:
                - INFO: External API call with service details, status, and timing
                - Performance metric recorded for monitoring
            """
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
            """Simulate authentication for audit logging demonstration.

            Demonstrates security audit logging for authentication attempts
            and authorization decisions. Critical for compliance and security
            monitoring.

            Returns:
                dict: Authentication status and user information.
                Status code 401 if authentication fails.

            Logs Generated:
                - INFO: Authentication attempt result (success/failure)
                - INFO: Authorization check result (if authenticated)
            """
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
            """Get logging configuration and statistics.

            Returns current logging system configuration including request ID,
            environment, log level, and handler information.

            Returns:
                dict: Logging system metadata and statistics.
            """
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
            """Get collected performance metrics and statistics.

            Returns aggregated performance data for various operations including
            database queries, external API calls, and cache operations.

            Returns:
                dict: Performance metrics with min, max, avg, and recent values
                    for each tracked operation type.
            """
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