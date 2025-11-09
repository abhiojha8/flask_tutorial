"""
Exercise 1: First Database Model - User Management API

OBJECTIVE:
Create your first database-backed Flask API with a single User table.

WHAT YOU'LL BUILD:
- SQLAlchemy User model
- Database connection to Supabase
- Complete CRUD API for users
- Proper error handling for database operations

LEARNING GOALS:
- Define database models with SQLAlchemy
- Connect Flask to PostgreSQL via Supabase
- Perform CRUD operations with ORM
- Handle database constraints (unique, not null)
- Manage database sessions

DATABASE SCHEMA:
users table:
- id: Integer, Primary Key, Auto-increment
- username: String(80), Unique, Not Null
- email: String(120), Unique, Not Null
- full_name: String(100), Nullable
- is_active: Boolean, Default True
- created_at: DateTime, Default UTC now
- updated_at: DateTime, Default UTC now, Auto-update on change

API ENDPOINTS:
- POST /users - Create new user
- GET /users - List all users
- GET /users/<id> - Get single user
- PUT /users/<id> - Update user
- DELETE /users/<id> - Delete user

TODO CHECKLIST:
[ ] Configure database connection from environment variables
[ ] Define User model with all required fields
[ ] Initialize database (create tables)
[ ] Implement POST /users (create user)
[ ] Implement GET /users (list all)
[ ] Implement GET /users/<id> (get one)
[ ] Implement PUT /users/<id> (update)
[ ] Implement DELETE /users/<id> (delete)
[ ] Add validation for unique constraints
[ ] Handle database errors gracefully
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    """
    Create and configure the User Management API.

    This is your first database-backed API!
    """
    app = Flask(__name__)
    CORS(app)

    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================

    # TODO: Configure database connection
    # HINT: Get DATABASE_URL from environment variables
    # HINT: Set SQLALCHEMY_TRACK_MODIFICATIONS to False (it's deprecated)

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables. Check your .env file!")

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking (saves memory)

    # Initialize Flask-RESTX for Swagger UI
    api = Api(
        app,
        version='1.0',
        title='User Management API',
        description='Exercise 1: First Database Model with SQLAlchemy',
        doc='/swagger'
    )

    # ============================================================================
    # DATABASE INITIALIZATION
    # ============================================================================

    # TODO: Initialize SQLAlchemy
    # HINT: Create db = SQLAlchemy(app)

    db = SQLAlchemy(app)

    # ============================================================================
    # DATABASE MODELS
    # ============================================================================

    # TODO: Define User model
    # HINT: class User(db.Model):
    # HINT: Use db.Column() for each field
    # HINT: Use db.Integer, db.String, db.Boolean, db.DateTime

    class User(db.Model):
        """
        User model representing a user in the system.

        This is your first SQLAlchemy model!
        Each class attribute becomes a database column.
        """
        __tablename__ = 'users'

        # TODO: Define all columns
        # HINT: id should be primary_key=True, autoincrement=True
        # HINT: username and email should have unique=True
        # HINT: created_at and updated_at should use datetime.utcnow as default

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        full_name = db.Column(db.String(100), nullable=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def to_dict(self):
            """
            Convert User object to dictionary for JSON serialization.

            WHY? SQLAlchemy objects can't be directly converted to JSON.
            We need to manually extract the data we want to return.
            """
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    # ============================================================================
    # CREATE TABLES
    # ============================================================================

    # Create all tables in the database
    # This runs when the app starts
    with app.app_context():
        db.create_all()
        print("[OK] Database tables created successfully!")

    # ============================================================================
    # API MODELS (for Swagger documentation)
    # ============================================================================

    users_ns = Namespace('users', description='User management operations')

    # Input model (what we expect when creating/updating)
    user_input_model = users_ns.model('UserInput', {
        'username': fields.String(required=True, description='Unique username', example='johndoe'),
        'email': fields.String(required=True, description='Unique email address', example='john@example.com'),
        'full_name': fields.String(required=False, description='Full name', example='John Doe'),
        'is_active': fields.Boolean(required=False, description='Active status', example=True)
    })

    # Output model (what we return)
    user_output_model = users_ns.model('User', {
        'id': fields.Integer(description='User ID'),
        'username': fields.String(description='Username'),
        'email': fields.String(description='Email'),
        'full_name': fields.String(description='Full name'),
        'is_active': fields.Boolean(description='Active status'),
        'created_at': fields.String(description='Creation timestamp'),
        'updated_at': fields.String(description='Last update timestamp')
    })

    # ============================================================================
    # API ENDPOINTS
    # ============================================================================

    @users_ns.route('/')
    class UserList(Resource):
        """User collection endpoints"""

        @users_ns.doc('list_users')
        @users_ns.marshal_list_with(user_output_model)
        def get(self):
            """List all users"""
            users = User.query.all()
            return [user.to_dict() for user in users]

        @users_ns.doc('create_user')
        @users_ns.expect(user_input_model)
        @users_ns.marshal_with(user_output_model, code=201)
        @users_ns.response(400, 'Validation Error')
        @users_ns.response(409, 'User already exists (duplicate username/email)')
        def post(self):
            """Create a new user"""
            data = request.json

            # Check for duplicate username
            if User.query.filter_by(username=data['username']).first():
                return {'message': 'Username already exists'}, 409

            # Check for duplicate email
            if User.query.filter_by(email=data['email']).first():
                return {'message': 'Email already exists'}, 409

            # Create new user
            user = User(
                username=data['username'],
                email=data['email'],
                full_name=data.get('full_name'),
                is_active=data.get('is_active', True)
            )

            db.session.add(user)
            db.session.commit()

            return user.to_dict(), 201

    @users_ns.route('/<int:id>')
    @users_ns.param('id', 'User identifier')
    class UserItem(Resource):
        """Single user endpoints"""

        @users_ns.doc('get_user')
        @users_ns.marshal_with(user_output_model)
        @users_ns.response(404, 'User not found')
        def get(self, id):
            """Get user by ID"""
            user = User.query.get_or_404(id)
            return user.to_dict()

        @users_ns.doc('update_user')
        @users_ns.expect(user_input_model)
        @users_ns.marshal_with(user_output_model)
        @users_ns.response(404, 'User not found')
        @users_ns.response(409, 'Duplicate username/email')
        def put(self, id):
            """Update user"""
            user = User.query.get_or_404(id)
            data = request.json

            # Check for duplicate username (excluding current user)
            if 'username' in data and data['username'] != user.username:
                if User.query.filter_by(username=data['username']).first():
                    return {'message': 'Username already exists'}, 409

            # Check for duplicate email (excluding current user)
            if 'email' in data and data['email'] != user.email:
                if User.query.filter_by(email=data['email']).first():
                    return {'message': 'Email already exists'}, 409

            # Update fields
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'is_active' in data:
                user.is_active = data['is_active']

            db.session.commit()
            return user.to_dict()

        @users_ns.doc('delete_user')
        @users_ns.response(204, 'User deleted successfully')
        @users_ns.response(404, 'User not found')
        def delete(self, id):
            """Delete user"""
            user = User.query.get_or_404(id)
            db.session.delete(user)
            db.session.commit()
            return '', 204

    # ============================================================================
    # REGISTER NAMESPACE
    # ============================================================================

    api.add_namespace(users_ns, path='/users')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("USER MANAGEMENT API - Exercise 1: First Database Model")
    print("="*70)
    print("📚 Learning Objectives:")
    print("  - Connect Flask to PostgreSQL/Supabase")
    print("  - Define SQLAlchemy models")
    print("  - Perform CRUD operations with ORM")
    print("  - Handle database constraints")
    print("\n🎯 Test Your Implementation:")
    print("  1. Create a user: POST /users")
    print("  2. List users: GET /users")
    print("  3. Get user: GET /users/1")
    print("  4. Update user: PUT /users/1")
    print("  5. Delete user: DELETE /users/1")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("🗄️  Check Supabase UI to see your data!")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
