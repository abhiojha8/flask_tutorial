"""
Flask API Demo Application with Swagger UI
A professional Flask API setup with automatic documentation
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from datetime import datetime
import logging
import sys
from werkzeug.exceptions import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    if config_name == 'development':
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
    elif config_name == 'testing':
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
    else:  # production
        app.config['DEBUG'] = False
        app.config['TESTING'] = False

    # Enable CORS
    CORS(app)

    # Initialize Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Task Management API',
        description='A professional Flask API with Swagger documentation',
        doc='/swagger',
        prefix='/api/v1'
    )

    # Create namespaces
    health_ns = Namespace('health', description='Health check operations')
    tasks_ns = Namespace('tasks', description='Task management operations')

    # Define models for documentation
    task_model = api.model('Task', {
        'id': fields.Integer(readonly=True, description='Task unique identifier'),
        'title': fields.String(required=True, description='Task title'),
        'description': fields.String(description='Task description'),
        'completed': fields.Boolean(description='Task completion status'),
        'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
        'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
    })

    task_input = api.model('TaskInput', {
        'title': fields.String(required=True, description='Task title', min_length=1, max_length=100),
        'description': fields.String(description='Task description', max_length=500),
        'completed': fields.Boolean(description='Task completion status', default=False)
    })

    # In-memory task storage (for demo purposes)
    tasks = []
    task_counter = {'id': 0}

    @health_ns.route('/')
    class HealthCheck(Resource):
        @health_ns.doc('health_check')
        def get(self):
            """Check if the API is running"""
            logger.info("Health check requested")
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'Task Management API',
                'version': '1.0'
            }

    @health_ns.route('/ready')
    class ReadinessCheck(Resource):
        @health_ns.doc('readiness_check')
        def get(self):
            """Check if the API is ready to serve requests"""
            # In production, check database connectivity, etc.
            return {
                'status': 'ready',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'database': 'ok',
                    'cache': 'ok'
                }
            }

    @tasks_ns.route('/')
    class TaskList(Resource):
        @tasks_ns.doc('list_tasks')
        @tasks_ns.marshal_list_with(task_model)
        def get(self):
            """List all tasks"""
            logger.info(f"Fetching all tasks. Count: {len(tasks)}")
            return tasks

        @tasks_ns.doc('create_task')
        @tasks_ns.expect(task_input, validate=True)
        @tasks_ns.marshal_with(task_model, code=201)
        def post(self):
            """Create a new task"""
            task_counter['id'] += 1
            new_task = {
                'id': task_counter['id'],
                'title': api.payload['title'],
                'description': api.payload.get('description', ''),
                'completed': api.payload.get('completed', False),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            tasks.append(new_task)
            logger.info(f"Created task with ID: {new_task['id']}")
            return new_task, 201

    @tasks_ns.route('/<int:task_id>')
    @tasks_ns.param('task_id', 'Task identifier')
    @tasks_ns.response(404, 'Task not found')
    class Task(Resource):
        @tasks_ns.doc('get_task')
        @tasks_ns.marshal_with(task_model)
        def get(self, task_id):
            """Get a task by ID"""
            task = next((t for t in tasks if t['id'] == task_id), None)
            if task is None:
                api.abort(404, f"Task {task_id} not found")
            logger.info(f"Retrieved task {task_id}")
            return task

        @tasks_ns.doc('update_task')
        @tasks_ns.expect(task_input, validate=True)
        @tasks_ns.marshal_with(task_model)
        def put(self, task_id):
            """Update a task"""
            task = next((t for t in tasks if t['id'] == task_id), None)
            if task is None:
                api.abort(404, f"Task {task_id} not found")

            task['title'] = api.payload.get('title', task['title'])
            task['description'] = api.payload.get('description', task['description'])
            task['completed'] = api.payload.get('completed', task['completed'])
            task['updated_at'] = datetime.utcnow()

            logger.info(f"Updated task {task_id}")
            return task

        @tasks_ns.doc('delete_task')
        @tasks_ns.response(204, 'Task deleted')
        def delete(self, task_id):
            """Delete a task"""
            global tasks
            initial_count = len(tasks)
            tasks = [t for t in tasks if t['id'] != task_id]

            if len(tasks) == initial_count:
                api.abort(404, f"Task {task_id} not found")

            logger.info(f"Deleted task {task_id}")
            return '', 204

    @tasks_ns.route('/search')
    class TaskSearch(Resource):
        @tasks_ns.doc('search_tasks')
        @tasks_ns.param('q', 'Search query', type='string')
        @tasks_ns.param('completed', 'Filter by completion status', type='boolean')
        @tasks_ns.marshal_list_with(task_model)
        def get(self):
            """Search tasks"""
            from flask import request
            query = request.args.get('q', '').lower()
            completed_filter = request.args.get('completed')

            results = tasks

            if query:
                results = [
                    t for t in results
                    if query in t['title'].lower() or query in t['description'].lower()
                ]

            if completed_filter is not None:
                completed_bool = completed_filter.lower() == 'true'
                results = [t for t in results if t['completed'] == completed_bool]

            logger.info(f"Search returned {len(results)} results")
            return results

    @tasks_ns.route('/stats')
    class TaskStats(Resource):
        @tasks_ns.doc('task_statistics')
        def get(self):
            """Get task statistics"""
            total = len(tasks)
            completed = sum(1 for t in tasks if t['completed'])
            pending = total - completed

            return {
                'total': total,
                'completed': completed,
                'pending': pending,
                'completion_rate': (completed / total * 100) if total > 0 else 0
            }

    # Register namespaces
    api.add_namespace(health_ns)
    api.add_namespace(tasks_ns)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'message': 'Internal server error'}, 500

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        logger.error(f"HTTP Exception: {e}")
        return {'message': e.description}, e.code

    # Add some sample data
    if config_name == 'development':
        sample_tasks = [
            {
                'id': 1,
                'title': 'Learn Flask',
                'description': 'Complete Chapter 1 of Flask tutorial',
                'completed': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'id': 2,
                'title': 'Build REST API',
                'description': 'Create a REST API with Swagger documentation',
                'completed': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'id': 3,
                'title': 'Setup Database',
                'description': 'Configure PostgreSQL for the project',
                'completed': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
        tasks.extend(sample_tasks)
        task_counter['id'] = 3
        logger.info(f"Loaded {len(sample_tasks)} sample tasks")

    return app


if __name__ == '__main__':
    app = create_app('development')
    logger.info("Starting Flask API server...")
    logger.info("Swagger UI available at: http://localhost:5000/swagger")
    app.run(host='0.0.0.0', port=5000, debug=True)