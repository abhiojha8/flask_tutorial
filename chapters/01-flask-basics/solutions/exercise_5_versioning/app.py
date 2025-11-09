"""
Flask API with comprehensive versioning system
Supports URL-based and header-based versioning
"""

from flask import Flask, request, g, jsonify
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
from datetime import datetime
import warnings


def create_app():
    """Create Flask app with API versioning"""
    app = Flask(__name__)

    # Configuration
    app.config['DEBUG'] = True
    app.config['API_VERSIONS'] = ['v1', 'v2', 'v3']
    app.config['DEFAULT_API_VERSION'] = 'v2'
    app.config['DEPRECATED_VERSIONS'] = ['v1']
    app.config['VERSION_SUNSET_DATES'] = {
        'v1': '2024-06-01',
        'v2': '2025-01-01'
    }

    # Enable CORS
    CORS(app)

    # Version detection middleware
    @app.before_request
    def detect_api_version():
        """Detect API version from URL or header"""
        # Try URL-based version first
        if request.path.startswith('/api/'):
            path_parts = request.path.split('/')
            if len(path_parts) > 2 and path_parts[2] in app.config['API_VERSIONS']:
                g.api_version = path_parts[2]
                return

        # Try header-based version
        header_version = request.headers.get('API-Version')
        if header_version:
            # Format: "v1", "1.0", "1"
            if header_version.startswith('v'):
                version = header_version
            else:
                version = f"v{header_version.split('.')[0]}"

            if version in app.config['API_VERSIONS']:
                g.api_version = version
            else:
                g.api_version = app.config['DEFAULT_API_VERSION']
        else:
            g.api_version = app.config['DEFAULT_API_VERSION']

    @app.after_request
    def add_version_headers(response):
        """Add API version information to response headers"""
        response.headers['X-API-Version'] = g.get('api_version', 'unknown')

        # Add deprecation warning for old versions
        if g.get('api_version') in app.config['DEPRECATED_VERSIONS']:
            sunset_date = app.config['VERSION_SUNSET_DATES'].get(g.api_version)
            response.headers['X-API-Deprecation'] = 'true'
            response.headers['X-API-Deprecation-Date'] = sunset_date
            response.headers['Warning'] = f'299 - "API version {g.api_version} is deprecated and will be removed on {sunset_date}"'

        return response

    # Create separate API instances for each version
    api_v1 = Api(
        app,
        version='1.0',
        title='API Version 1 (Deprecated)',
        description='Legacy API version - will be removed on 2024-06-01',
        doc='/api/v1/swagger',
        prefix='/api/v1'
    )

    api_v2 = Api(
        app,
        version='2.0',
        title='API Version 2 (Current)',
        description='Current stable API version',
        doc='/api/v2/swagger',
        prefix='/api/v2'
    )

    api_v3 = Api(
        app,
        version='3.0',
        title='API Version 3 (Beta)',
        description='Next generation API with breaking changes',
        doc='/api/v3/swagger',
        prefix='/api/v3'
    )

    # Version 1 Endpoints (Legacy)
    tasks_v1 = Namespace('tasks', description='Task operations (v1)')

    task_model_v1 = api_v1.model('Task', {
        'id': fields.Integer(readonly=True),
        'name': fields.String(required=True),  # Changed to 'title' in v2
        'done': fields.Boolean()  # Changed to 'completed' in v2
    })

    @tasks_v1.route('/')
    class TaskListV1(Resource):
        @tasks_v1.doc('list_tasks')
        @tasks_v1.marshal_list_with(task_model_v1)
        def get(self):
            """List all tasks (v1 format)"""
            # Legacy format with deprecated field names
            return [
                {'id': 1, 'name': 'Task One', 'done': False},
                {'id': 2, 'name': 'Task Two', 'done': True}
            ]

        @tasks_v1.doc('create_task')
        @tasks_v1.expect(task_model_v1)
        @tasks_v1.marshal_with(task_model_v1, code=201)
        def post(self):
            """Create a task (v1 format)"""
            # Note: v1 doesn't support priority field
            return {'id': 3, 'name': api_v1.payload['name'], 'done': False}, 201

    api_v1.add_namespace(tasks_v1)

    # Version 2 Endpoints (Current)
    tasks_v2 = Namespace('tasks', description='Task operations (v2)')

    task_model_v2 = api_v2.model('Task', {
        'id': fields.Integer(readonly=True),
        'title': fields.String(required=True),  # Renamed from 'name'
        'description': fields.String(),  # New field in v2
        'completed': fields.Boolean(),  # Renamed from 'done'
        'priority': fields.String(enum=['low', 'medium', 'high']),  # New in v2
        'created_at': fields.DateTime(readonly=True)  # New in v2
    })

    @tasks_v2.route('/')
    class TaskListV2(Resource):
        @tasks_v2.doc('list_tasks')
        @tasks_v2.marshal_list_with(task_model_v2)
        @tasks_v2.param('priority', 'Filter by priority', enum=['low', 'medium', 'high'])
        def get(self):
            """List all tasks with filtering (v2 format)"""
            priority = request.args.get('priority')
            tasks = [
                {
                    'id': 1,
                    'title': 'Task One',
                    'description': 'First task description',
                    'completed': False,
                    'priority': 'high',
                    'created_at': datetime.utcnow()
                },
                {
                    'id': 2,
                    'title': 'Task Two',
                    'description': 'Second task description',
                    'completed': True,
                    'priority': 'low',
                    'created_at': datetime.utcnow()
                }
            ]

            if priority:
                tasks = [t for t in tasks if t['priority'] == priority]

            return tasks

        @tasks_v2.doc('create_task')
        @tasks_v2.expect(task_model_v2)
        @tasks_v2.marshal_with(task_model_v2, code=201)
        def post(self):
            """Create a task with priority (v2 format)"""
            task = api_v2.payload
            task['id'] = 3
            task['created_at'] = datetime.utcnow()
            task['completed'] = task.get('completed', False)
            return task, 201

    @tasks_v2.route('/<int:task_id>')
    @tasks_v2.param('task_id', 'Task identifier')
    class TaskV2(Resource):
        @tasks_v2.doc('get_task')
        @tasks_v2.marshal_with(task_model_v2)
        def get(self, task_id):
            """Get task by ID (v2 feature)"""
            return {
                'id': task_id,
                'title': f'Task {task_id}',
                'description': 'Task description',
                'completed': False,
                'priority': 'medium',
                'created_at': datetime.utcnow()
            }

    api_v2.add_namespace(tasks_v2)

    # Version 3 Endpoints (Beta with Breaking Changes)
    tasks_v3 = Namespace('tasks', description='Task operations (v3)')

    # V3 uses nested objects and different structure
    user_model_v3 = api_v3.model('User', {
        'id': fields.Integer(),
        'name': fields.String(),
        'email': fields.String()
    })

    task_model_v3 = api_v3.model('Task', {
        'id': fields.String(readonly=True),  # Changed to UUID string in v3
        'title': fields.String(required=True),
        'description': fields.String(),
        'status': fields.String(enum=['pending', 'in_progress', 'completed', 'cancelled']),  # Expanded from boolean
        'priority': fields.Integer(min=1, max=5),  # Changed to numeric priority
        'assignee': fields.Nested(user_model_v3),  # New nested object
        'tags': fields.List(fields.String()),  # New field
        'metadata': fields.Raw(),  # Flexible metadata field
        'created_at': fields.DateTime(readonly=True),
        'updated_at': fields.DateTime(readonly=True)
    })

    @tasks_v3.route('/')
    class TaskListV3(Resource):
        @tasks_v3.doc('list_tasks')
        @tasks_v3.marshal_list_with(task_model_v3)
        @tasks_v3.param('status', 'Filter by status')
        @tasks_v3.param('assignee_id', 'Filter by assignee')
        def get(self):
            """List tasks with advanced filtering (v3 format)"""
            return [
                {
                    'id': 'uuid-123-456',
                    'title': 'Task One',
                    'description': 'First task with assignee',
                    'status': 'in_progress',
                    'priority': 4,
                    'assignee': {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
                    'tags': ['urgent', 'backend'],
                    'metadata': {'client': 'ACME Corp', 'project': 'API'},
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            ]

        @tasks_v3.doc('create_task')
        @tasks_v3.expect(task_model_v3)
        @tasks_v3.marshal_with(task_model_v3, code=201)
        def post(self):
            """Create task with full metadata (v3 format)"""
            import uuid
            task = api_v3.payload
            task['id'] = str(uuid.uuid4())
            task['created_at'] = datetime.utcnow()
            task['updated_at'] = datetime.utcnow()
            return task, 201

    api_v3.add_namespace(tasks_v3)

    # Version information endpoint
    @app.route('/api/versions')
    def get_versions():
        """Get API version information"""
        return jsonify({
            'current_version': g.get('api_version'),
            'available_versions': app.config['API_VERSIONS'],
            'default_version': app.config['DEFAULT_API_VERSION'],
            'deprecated_versions': app.config['DEPRECATED_VERSIONS'],
            'sunset_dates': app.config['VERSION_SUNSET_DATES'],
            'documentation': {
                'v1': '/api/v1/swagger',
                'v2': '/api/v2/swagger',
                'v3': '/api/v3/swagger'
            },
            'migration_guide': 'https://api.example.com/docs/migration'
        })

    # Version migration helper endpoint
    @app.route('/api/migrate')
    def migration_guide():
        """Get migration guide between versions"""
        from_version = request.args.get('from', 'v1')
        to_version = request.args.get('to', 'v2')

        guides = {
            'v1_to_v2': {
                'breaking_changes': [
                    'Field "name" renamed to "title"',
                    'Field "done" renamed to "completed"',
                    'New required field "priority"',
                    'Date fields now in ISO format'
                ],
                'new_features': [
                    'Task filtering by priority',
                    'Task description field',
                    'Created_at timestamp',
                    'GET /tasks/{id} endpoint'
                ],
                'deprecated': [
                    'Field "name" (use "title")',
                    'Field "done" (use "completed")'
                ]
            },
            'v2_to_v3': {
                'breaking_changes': [
                    'Task ID changed from integer to UUID string',
                    'Priority changed from string to integer (1-5)',
                    'Status expanded from boolean to enum',
                    'Assignee is now a nested object'
                ],
                'new_features': [
                    'Task assignee support',
                    'Tags for categorization',
                    'Flexible metadata field',
                    'Updated_at timestamp'
                ],
                'deprecated': [
                    'Boolean "completed" field (use "status")',
                    'String priority (use numeric 1-5)'
                ]
            }
        }

        migration_key = f"{from_version}_to_{to_version}"
        if migration_key in guides:
            return jsonify({
                'from': from_version,
                'to': to_version,
                'guide': guides[migration_key]
            })
        else:
            return jsonify({
                'error': 'No migration guide available',
                'from': from_version,
                'to': to_version
            }), 404

    return app


if __name__ == '__main__':
    app = create_app()

    print("\n" + "="*70)
    print("API Versioning Demo")
    print("="*70)
    print("Available API Versions:")
    print("  - v1 (Deprecated): http://localhost:5000/api/v1/swagger")
    print("  - v2 (Current):    http://localhost:5000/api/v2/swagger")
    print("  - v3 (Beta):       http://localhost:5000/api/v3/swagger")
    print("\nVersion Information:")
    print("  - http://localhost:5000/api/versions")
    print("  - http://localhost:5000/api/migrate?from=v1&to=v2")
    print("\nTesting:")
    print("  - URL-based:    curl http://localhost:5000/api/v2/tasks/")
    print("  - Header-based: curl -H 'API-Version: v2' http://localhost:5000/api/tasks/")
    print("="*70 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)