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
    """
    Create and configure the Flask application using the factory pattern.

    This pattern allows for easy testing and multiple configurations.
    It's a best practice for Flask applications that may grow in complexity.

    Args:
        config_name (str): The configuration environment to use.
                          Options: 'development', 'testing', 'production'
                          Defaults to 'development'.

    Returns:
        Flask: A configured Flask application instance with:
               - CORS enabled for cross-origin requests
               - Flask-RESTX API with Swagger UI at /swagger
               - Configured namespaces for different API sections
               - Sample data loaded (in development mode)

    Example:
        app = create_app('development')
        app.run(debug=True)
    """
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
        """
        Health check endpoint for monitoring API status.

        This endpoint provides a simple way to check if the API is running
        and responsive. It's commonly used by load balancers and monitoring
        tools to determine service health.
        """

        @health_ns.doc('health_check')
        def get(self):
            """
            Perform a basic health check of the API.

            Returns a simple health status indicating the API is running.
            This is typically used for liveness probes in container orchestration.

            Returns:
                dict: Health status with timestamp and service information
                    - status (str): Always 'healthy' if the service responds
                    - timestamp (str): Current UTC timestamp in ISO format
                    - service (str): Name of the service
                    - version (str): API version
            """
            logger.info("Health check requested")
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'Task Management API',
                'version': '1.0'
            }

    @health_ns.route('/ready')
    class ReadinessCheck(Resource):
        """
        Readiness check endpoint for determining if the API can serve requests.

        Different from health check, this endpoint verifies that all dependencies
        (database, cache, external services) are available and the service is
        ready to handle traffic.
        """

        @health_ns.doc('readiness_check')
        def get(self):
            """
            Check if the API is ready to serve requests.

            Verifies that all required services and dependencies are available.
            In production, this would check database connections, cache availability,
            and other critical dependencies.

            Returns:
                dict: Readiness status with individual component health
                    - status (str): 'ready' if all checks pass
                    - timestamp (str): Current UTC timestamp
                    - checks (dict): Status of each component
            """
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
        """
        Task collection endpoint for managing multiple tasks.

        Handles operations on the entire task collection including
        listing all tasks and creating new tasks.
        """

        @tasks_ns.doc('list_tasks')
        @tasks_ns.marshal_list_with(task_model)
        def get(self):
            """
            Retrieve all tasks in the system.

            Returns a list of all tasks currently stored in memory.
            In a production system, this would typically include pagination
            parameters to handle large datasets efficiently.

            Returns:
                list: Array of task objects, each containing:
                    - id (int): Unique task identifier
                    - title (str): Task title
                    - description (str): Task description
                    - completed (bool): Completion status
                    - created_at (datetime): Creation timestamp
                    - updated_at (datetime): Last modification timestamp
            """
            logger.info(f"Fetching all tasks. Count: {len(tasks)}")
            return tasks

        @tasks_ns.doc('create_task')
        @tasks_ns.expect(task_input, validate=True)
        @tasks_ns.marshal_with(task_model, code=201)
        def post(self):
            """
            Create a new task.

            Accepts task data in the request body and creates a new task
            with auto-generated ID and timestamps. The task is stored in
            the in-memory list (in production, this would persist to a database).

            Returns:
                tuple: (task_dict, 201) - Created task with 201 status code
                    The task includes all fields plus generated ID and timestamps

            Raises:
                400: If validation fails (handled by Flask-RESTX validate=True)
            """
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
        """
        Individual task endpoint for single task operations.

        Handles CRUD operations on individual tasks identified by their ID.
        Supports retrieving, updating, and deleting specific tasks.
        """

        @tasks_ns.doc('get_task')
        @tasks_ns.marshal_with(task_model)
        def get(self, task_id):
            """
            Retrieve a specific task by its ID.

            Args:
                task_id (int): Unique identifier of the task to retrieve

            Returns:
                dict: Task object if found

            Raises:
                404: If task with given ID does not exist
            """
            task = next((t for t in tasks if t['id'] == task_id), None)
            if task is None:
                api.abort(404, f"Task {task_id} not found")
            logger.info(f"Retrieved task {task_id}")
            return task

        @tasks_ns.doc('update_task')
        @tasks_ns.expect(task_input, validate=True)
        @tasks_ns.marshal_with(task_model)
        def put(self, task_id):
            """
            Update an existing task.

            Performs a partial update on the task. Only provided fields
            are updated; omitted fields retain their current values.
            Updates the 'updated_at' timestamp automatically.

            Args:
                task_id (int): ID of the task to update

            Returns:
                dict: Updated task object

            Raises:
                404: If task with given ID does not exist
                400: If validation fails on input data
            """
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
            """
            Delete a task permanently.

            Removes the task from the system. This is a permanent operation
            and cannot be undone. Returns 204 No Content on success.

            Args:
                task_id (int): ID of the task to delete

            Returns:
                tuple: ('', 204) - Empty response with 204 status code

            Raises:
                404: If task with given ID does not exist
            """
            global tasks
            initial_count = len(tasks)
            tasks = [t for t in tasks if t['id'] != task_id]

            if len(tasks) == initial_count:
                api.abort(404, f"Task {task_id} not found")

            logger.info(f"Deleted task {task_id}")
            return '', 204

    @tasks_ns.route('/search')
    class TaskSearch(Resource):
        """
        Task search endpoint with filtering capabilities.

        Provides search functionality across task titles and descriptions,
        with optional filtering by completion status.
        """

        @tasks_ns.doc('search_tasks')
        @tasks_ns.param('q', 'Search query', type='string')
        @tasks_ns.param('completed', 'Filter by completion status', type='boolean')
        @tasks_ns.marshal_list_with(task_model)
        def get(self):
            """
            Search tasks by query string and filter by status.

            Performs case-insensitive search across task titles and descriptions.
            Optionally filters results by completion status.

            Query Parameters:
                q (str, optional): Search query to match against title/description
                completed (bool, optional): Filter by completion status

            Returns:
                list: Array of tasks matching search criteria

            Example:
                GET /api/v1/tasks/search?q=important&completed=false
                Returns all incomplete tasks containing 'important'
            """
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
        """
        Task statistics endpoint for analytics.

        Provides aggregated statistics about tasks in the system,
        useful for dashboards and reporting.
        """

        @tasks_ns.doc('task_statistics')
        def get(self):
            """
            Get aggregated statistics about tasks.

            Calculates and returns various metrics about the tasks,
            including counts and completion rates.

            Returns:
                dict: Statistics object containing:
                    - total (int): Total number of tasks
                    - completed (int): Number of completed tasks
                    - pending (int): Number of pending tasks
                    - completion_rate (float): Percentage of tasks completed
            """
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