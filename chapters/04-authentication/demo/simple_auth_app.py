"""
SIMPLE AUTHENTICATION DEMO
Chapter 4: Authentication Basics

This is a simplified authentication app focused on teaching core concepts:
- User registration with password hashing
- Login with JWT tokens
- Protected routes
- Password validation

SIMPLIFIED ARCHITECTURE:
- Only 1 model: User
- Core endpoints: register, login, get profile
- Clear examples of authentication patterns

DATABASE SCHEMA:
users_simple:
  - id, username, email, password_hash
  - created_at

Run with: python simple_auth_app.py
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import re
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# ============================================================================
# APP SETUP
# ============================================================================

app = Flask(__name__)
CORS(app)

# Configuration
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL not found in environment variables!")

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-me')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# API
api = Api(
    app,
    version='1.0',
    title='Simple Auth API',
    description='Simplified authentication demo for learning',
    doc='/docs'
)

# ============================================================================
# DATABASE MODEL
# ============================================================================

class User(db.Model):
    """
    Simple User model with authentication essentials.

    Key fields:
    - password_hash: NEVER store plain passwords!
    - email: Used for login (must be unique)
    """
    __tablename__ = 'users_simple'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash password using bcrypt."""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self):
        """Convert to dictionary (NEVER include password_hash!)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Create tables
with app.app_context():
    db.create_all()
    print("[OK] Database table created!")

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_email(email):
    """Check if email format is valid."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Check password meets requirements:
    - At least 8 characters
    - Contains a number
    - Contains a letter
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"

    return True, None

# ============================================================================
# API MODELS (Swagger Documentation)
# ============================================================================

auth_ns = Namespace('auth', description='Authentication operations')

# Request models
register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, example='johndoe'),
    'email': fields.String(required=True, example='john@example.com'),
    'password': fields.String(required=True, example='password123')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, example='john@example.com'),
    'password': fields.String(required=True, example='password123')
})

# Response models
user_model = auth_ns.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email'),
    'created_at': fields.String(description='Registration date')
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='JWT access token'),
    'token_type': fields.String(example='Bearer'),
    'expires_in': fields.Integer(example=3600)
})

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model, validate=True)
    @auth_ns.marshal_with(user_model, code=201)
    def post(self):
        """
        Register a new user.

        Steps:
        1. Validate email format
        2. Validate password strength
        3. Check for duplicates
        4. Hash password with bcrypt
        5. Create user

        Security: Password is hashed before storage using bcrypt.
        """
        data = request.json

        # Validate email
        if not validate_email(data['email']):
            return {'error': 'Invalid email format'}, 400

        # Validate password
        is_valid, error_msg = validate_password(data['password'])
        if not is_valid:
            return {'error': error_msg}, 400

        # Check duplicates
        if User.query.filter_by(username=data['username']).first():
            return {'error': 'Username already exists'}, 409

        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email already exists'}, 409

        # Create user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])  # Hash the password!

        db.session.add(user)
        db.session.commit()

        return user.to_dict(), 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.marshal_with(token_model)
    def post(self):
        """
        Login and get JWT token.

        Steps:
        1. Find user by email
        2. Verify password
        3. Generate JWT token
        4. Return token

        Use the token in subsequent requests:
        Header: Authorization: Bearer <access_token>
        """
        data = request.json

        # Find user
        user = User.query.filter_by(email=data['email']).first()

        # Verify credentials
        if not user or not user.check_password(data['password']):
            return {'error': 'Invalid email or password'}, 401

        # Create JWT token with user ID as identity
        access_token = create_access_token(identity=user.id)

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1 hour
        }, 200


@auth_ns.route('/me')
class Profile(Resource):
    @auth_ns.doc(security='apikey')
    @auth_ns.marshal_with(user_model)
    @jwt_required()  # This decorator protects the route
    def get(self):
        """
        Get current user profile (protected route).

        This demonstrates:
        - Protected route with @jwt_required()
        - Extracting user from JWT token
        - Returning user data

        Must include header: Authorization: Bearer <token>
        """
        # Extract user ID from JWT token
        user_id = get_jwt_identity()

        # Fetch user from database
        user = User.query.get(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        return user.to_dict(), 200

# ============================================================================
# REGISTER NAMESPACE
# ============================================================================

api.add_namespace(auth_ns, path='/api/auth')

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SIMPLE AUTHENTICATION DEMO")
    print("="*70)
    print("\n✨ CORE CONCEPTS:")
    print("  ✅ Password hashing with bcrypt")
    print("  ✅ JWT token authentication")
    print("  ✅ Protected routes with @jwt_required()")
    print("  ✅ User registration and login")
    print("\n🚀 TRY IT OUT:")
    print("  1. Register: POST /api/auth/register")
    print("     {\"username\": \"john\", \"email\": \"john@example.com\", \"password\": \"password123\"}")
    print("\n  2. Login: POST /api/auth/login")
    print("     {\"email\": \"john@example.com\", \"password\": \"password123\"}")
    print("\n  3. Get Profile: GET /api/auth/me")
    print("     Header: Authorization: Bearer <your_token>")
    print("\n📚 KEY LEARNING POINTS:")
    print("  • NEVER store passwords in plain text")
    print("  • Use bcrypt for password hashing")
    print("  • JWT tokens are stateless (no database lookup)")
    print("  • Token contains user identity (user_id)")
    print("  • Protected routes require valid token")
    print("\n🌐 API Docs: http://localhost:5000/docs")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
