"""
Flask API with comprehensive error handling
Demonstrates custom exceptions and global error handlers
"""

from flask import Flask, g, request
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
import uuid
from handlers import register_error_handlers
from exceptions import (
    NotFoundError, ValidationError, UnauthorizedError,
    ForbiddenError, ConflictError, RateLimitError,
    ExternalServiceError, BusinessLogicError
)


def create_app():
    """Create Flask app with error handling"""
    app = Flask(__name__)

    # Configuration
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = False

    # Set up request ID tracking
    @app.before_request
    def before_request():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

    # Register error handlers
    register_error_handlers(app)

    # Enable CORS
    CORS(app)

    # Initialize Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Error Handling Demo API',
        description='API demonstrating comprehensive error handling',
        doc='/swagger',
        prefix='/api/v1'
    )

    # Create namespace
    demo_ns = Namespace('demo', description='Error demonstration endpoints')

    # Define models
    user_model = api.model('User', {
        'id': fields.Integer(readonly=True),
        'email': fields.String(required=True),
        'name': fields.String(required=True)
    })

    # Sample data
    users = [
        {'id': 1, 'email': 'user1@example.com', 'name': 'User One'},
        {'id': 2, 'email': 'user2@example.com', 'name': 'User Two'}
    ]

    @demo_ns.route('/users/<int:user_id>')
    @demo_ns.param('user_id', 'User identifier')
    class User(Resource):
        @demo_ns.doc('get_user')
        @demo_ns.marshal_with(user_model)
        def get(self, user_id):
            """Get user by ID - demonstrates NotFoundError"""
            user = next((u for u in users if u['id'] == user_id), None)
            if not user:
                raise NotFoundError(resource='User', resource_id=user_id)
            return user

    @demo_ns.route('/validation')
    class ValidationDemo(Resource):
        @demo_ns.doc('validation_demo')
        @demo_ns.expect(user_model)
        def post(self):
            """Create user with validation - demonstrates ValidationError"""
            data = api.payload

            # Validation checks
            errors = {}
            if not data.get('email'):
                errors['email'] = 'Email is required'
            elif '@' not in data.get('email', ''):
                errors['email'] = 'Invalid email format'

            if not data.get('name'):
                errors['name'] = 'Name is required'
            elif len(data.get('name', '')) < 2:
                errors['name'] = 'Name must be at least 2 characters'

            if errors:
                raise ValidationError(errors=errors)

            # Check for duplicate email
            if any(u['email'] == data.get('email') for u in users):
                raise ConflictError(resource='User', conflict_field='email')

            return {'message': 'Validation passed', 'data': data}

    @demo_ns.route('/unauthorized')
    class UnauthorizedDemo(Resource):
        @demo_ns.doc('unauthorized_demo')
        def get(self):
            """Demonstrates UnauthorizedError"""
            # Simulate missing authentication
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                raise UnauthorizedError(
                    message='Authentication required',
                    auth_type='Bearer'
                )
            return {'message': 'Authorized'}

    @demo_ns.route('/forbidden')
    class ForbiddenDemo(Resource):
        @demo_ns.doc('forbidden_demo')
        def delete(self):
            """Demonstrates ForbiddenError"""
            # Simulate permission check
            raise ForbiddenError(resource='admin_panel', action='delete')

    @demo_ns.route('/rate-limit')
    class RateLimitDemo(Resource):
        @demo_ns.doc('rate_limit_demo')
        def get(self):
            """Demonstrates RateLimitError"""
            # Simulate rate limit check
            import random
            if random.choice([True, False]):
                raise RateLimitError(
                    limit=100,
                    window='1 hour',
                    retry_after=3600
                )
            return {'message': 'Request allowed'}

    @demo_ns.route('/external-service')
    class ExternalServiceDemo(Resource):
        @demo_ns.doc('external_service_demo')
        def get(self):
            """Demonstrates ExternalServiceError"""
            # Simulate external service failure
            try:
                # Simulate external API call
                import random
                if random.choice([True, False]):
                    raise ConnectionError('Connection timeout')
            except ConnectionError as e:
                raise ExternalServiceError(
                    service='payment-gateway',
                    error=e
                )
            return {'message': 'External service responded'}

    @demo_ns.route('/business-logic')
    class BusinessLogicDemo(Resource):
        @demo_ns.doc('business_logic_demo')
        def post(self):
            """Demonstrates BusinessLogicError"""
            data = api.payload or {}
            amount = data.get('amount', 0)

            # Business rule: minimum transaction amount
            if amount < 10:
                raise BusinessLogicError(
                    rule='minimum_transaction',
                    message='Transaction amount must be at least $10'
                )

            # Business rule: maximum transaction amount
            if amount > 10000:
                raise BusinessLogicError(
                    rule='maximum_transaction',
                    message='Transaction amount cannot exceed $10,000'
                )

            return {'message': 'Business rules validated', 'amount': amount}

    @demo_ns.route('/trigger-500')
    class InternalErrorDemo(Resource):
        @demo_ns.doc('internal_error_demo')
        def get(self):
            """Demonstrates 500 Internal Server Error"""
            # Intentionally cause an error
            result = 1 / 0
            return {'result': result}

    @demo_ns.route('/trigger-value-error')
    class ValueErrorDemo(Resource):
        @demo_ns.doc('value_error_demo')
        def get(self):
            """Demonstrates ValueError handling"""
            # Intentionally cause a ValueError
            int('not_a_number')
            return {'message': 'This should not be reached'}

    @demo_ns.route('/trigger-key-error')
    class KeyErrorDemo(Resource):
        @demo_ns.doc('key_error_demo')
        def get(self):
            """Demonstrates KeyError handling"""
            # Intentionally cause a KeyError
            data = {}
            value = data['non_existent_key']
            return {'value': value}

    # Register namespace
    api.add_namespace(demo_ns)

    return app


if __name__ == '__main__':
    app = create_app()

    print("\n" + "="*60)
    print("Error Handling Demo API")
    print("="*60)
    print("Swagger UI: http://localhost:5000/swagger")
    print("\nTest error handling with these endpoints:")
    print("  - GET    /api/v1/demo/users/999       (404 Not Found)")
    print("  - POST   /api/v1/demo/validation      (400 Validation)")
    print("  - GET    /api/v1/demo/unauthorized    (401 Unauthorized)")
    print("  - DELETE /api/v1/demo/forbidden       (403 Forbidden)")
    print("  - GET    /api/v1/demo/rate-limit      (429 Rate Limit)")
    print("  - GET    /api/v1/demo/trigger-500     (500 Server Error)")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)