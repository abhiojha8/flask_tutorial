"""
Exercise 4: Error Handling and Status Codes

Learning Objectives:
- Handle different error scenarios
- Return appropriate HTTP status codes
- Create custom error responses
- Use api.abort for proper error handling

TODO: Complete the marked sections!
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

    # TODO 1: Create helper function to find user by id
    # def find_user(user_id):
    #     """Find a user by ID, return None if not found."""
    #     # Loop through users and return user if id matches
    #     # Return None if not found


    # TODO 2: Create helper function to find user by username
    # def find_user_by_username(username):
    #     """Find a user by username, return None if not found."""
    #     # Loop through users and return user if username matches


    # TODO 3: Create UserList Resource
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
            """
            Create a new user with validation.

            TODO: Implement the following validations:
            """
            data = api.payload

            # TODO 3a: Check if username already exists
            # Hint: Use find_user_by_username()
            # If exists, return: api.abort(409, f"Username '{username}' already exists")


            # TODO 3b: Validate email format (must contain @)
            # Hint: if '@' not in data['email']:
            # If invalid, return: api.abort(400, "Invalid email format")


            # TODO 3c: Validate age if provided (must be between 0 and 150)
            # Hint: if 'age' in data and (data['age'] < 0 or data['age'] > 150):
            # If invalid, return: api.abort(400, "Age must be between 0 and 150")


            # TODO 3d: Create user with id and created_at
            # Hint: new_id = len(users) + 1
            # Hint: user = {'id': new_id, 'created_at': datetime.now().isoformat(), ...}


            # TODO 3e: Add to users list and return with 201
            # Hint: users.append(user)
            # Hint: return user, 201


    # TODO 4: Create User Resource (single user operations)
    @users_ns.route('/<int:id>')
    @users_ns.param('id', 'The user identifier')
    @users_ns.response(404, 'User not found')
    class User(Resource):
        @users_ns.doc('get_user')
        @users_ns.marshal_with(user_output)
        def get(self, id):
            """
            Get a user by ID.

            TODO: Implement with proper error handling
            """
            # TODO 4a: Find user by id
            # Hint: user = find_user(id)


            # TODO 4b: Return 404 if not found
            # Hint: if not user: api.abort(404, f"User {id} not found")


            # TODO 4c: Return user


        @users_ns.doc('update_user')
        @users_ns.expect(user_input)
        @users_ns.marshal_with(user_output)
        @users_ns.response(409, 'Username already exists')
        def put(self, id):
            """
            Update a user.

            TODO: Implement with validation
            """
            # TODO 4d: Find user by id
            # Return 404 if not found


            data = api.payload

            # TODO 4e: If username is changing, check if new username exists
            # Hint: if data['username'] != user['username']:
            # Hint: Check if new username exists in another user


            # TODO 4f: Validate email format


            # TODO 4g: Update user fields
            # Hint: user['username'] = data['username']
            # Keep id and created_at unchanged!


            # TODO 4h: Return updated user


        @users_ns.doc('delete_user')
        @users_ns.response(204, 'User deleted')
        def delete(self, id):
            """
            Delete a user.

            TODO: Implement with proper error handling
            """
            # TODO 4i: Find user


            # TODO 4j: Return 404 if not found


            # TODO 4k: Remove from users list
            # Hint: users.remove(user)


            # TODO 4l: Return 204 No Content
            # Hint: return '', 204


    api.add_namespace(users_ns, path='/users')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 4: Error Handling and Status Codes")
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
