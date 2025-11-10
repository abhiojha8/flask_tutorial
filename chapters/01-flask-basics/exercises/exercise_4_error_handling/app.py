"""
Exercise 4 Solution: Error Handling and Status Codes

This solution demonstrates:
- Handling different error scenarios
- Returning appropriate HTTP status codes
- Using api.abort for proper error responses
- Validating business logic
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime

def create_app():
    """Create the Flask application."""
    app = Flask(__name__)

    api = Api(
        app,
        title='User API',
        version='1.0',
        description='API demonstrating error handling',
        doc='/swagger'
    )

    users_ns = Namespace('users', description='User operations')

    # Data models
    user_input = api.model('UserInput', {
        'username': fields.String(required=True, description='Username', min_length=3, max_length=20),
        'email': fields.String(required=True, description='Email'),
        'age': fields.Integer(description='Age', min=0, max=150)
    })

    user_output = api.inherit('UserOutput', user_input, {
        'id': fields.Integer(readonly=True, description='User ID'),
        'created_at': fields.String(readonly=True, description='Creation timestamp')
    })

    # In-memory storage
    users = []

    # Helper functions
    def find_user(user_id):
        """Find a user by ID, return None if not found."""
        for user in users:
            if user['id'] == user_id:
                return user
        return None

    def find_user_by_username(username):
        """Find a user by username, return None if not found."""
        for user in users:
            if user['username'] == username:
                return user
        return None

    # UserList Resource
    @users_ns.route('/')
    class UserList(Resource):
        @users_ns.doc('list_users')
        @users_ns.marshal_list_with(user_output)
        def get(self):
            """List all users"""
            return users

        @users_ns.doc('create_user')
        @users_ns.expect(user_input, validate=True)
        @users_ns.marshal_with(user_output, code=201)
        @users_ns.response(409, 'Username already exists')
        @users_ns.response(400, 'Invalid email format')
        def post(self):
            """Create a new user with validation."""
            data = api.payload

            # Check if username already exists
            if find_user_by_username(data['username']):
                api.abort(409, f"Username '{data['username']}' already exists")

            # Validate email format (must contain @)
            if '@' not in data['email']:
                api.abort(400, "Invalid email format")

            # Validate age if provided
            if 'age' in data and (data['age'] < 0 or data['age'] > 150):
                api.abort(400, "Age must be between 0 and 150")

            # Create user
            new_id = len(users) + 1
            user = {
                'id': new_id,
                'username': data['username'],
                'email': data['email'],
                'age': data.get('age'),
                'created_at': datetime.now().isoformat()
            }

            users.append(user)
            return user, 201

    # User Resource (single user operations)
    @users_ns.route('/<int:id>')
    @users_ns.param('id', 'The user identifier')
    @users_ns.response(404, 'User not found')
    class User(Resource):
        @users_ns.doc('get_user')
        @users_ns.marshal_with(user_output)
        def get(self, id):
            """Get a user by ID."""
            user = find_user(id)
            if not user:
                api.abort(404, f"User {id} not found")
            return user

        @users_ns.doc('update_user')
        @users_ns.expect(user_input)
        @users_ns.marshal_with(user_output)
        @users_ns.response(409, 'Username already exists')
        def put(self, id):
            """Update a user."""
            user = find_user(id)
            if not user:
                api.abort(404, f"User {id} not found")

            data = api.payload

            # If username is changing, check if new username exists
            if data['username'] != user['username']:
                existing = find_user_by_username(data['username'])
                if existing:
                    api.abort(409, f"Username '{data['username']}' already exists")

            # Validate email format
            if '@' not in data['email']:
                api.abort(400, "Invalid email format")

            # Validate age if provided
            if 'age' in data and (data['age'] < 0 or data['age'] > 150):
                api.abort(400, "Age must be between 0 and 150")

            # Update user fields
            user['username'] = data['username']
            user['email'] = data['email']
            user['age'] = data.get('age')
            # Keep id and created_at unchanged

            return user

        @users_ns.doc('delete_user')
        @users_ns.response(204, 'User deleted')
        def delete(self, id):
            """Delete a user."""
            user = find_user(id)
            if not user:
                api.abort(404, f"User {id} not found")

            users.remove(user)
            return '', 204

    api.add_namespace(users_ns, path='/users')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 4 Solution: Error Handling and Status Codes")
    print("="*50)
    print("Swagger UI: http://localhost:5000/swagger")
    print("\nTest these error scenarios:")
    print("  1. Create user with duplicate username (409)")
    print("  2. Create user with invalid email (400)")
    print("  3. Create user with age > 150 (400)")
    print("  4. Get non-existent user (404)")
    print("  5. Update to existing username (409)")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
