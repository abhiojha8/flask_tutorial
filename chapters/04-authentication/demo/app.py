"""
DEMO: Secure Blog Platform with JWT Authentication
Chapter 4: Authentication & Authorization

This demo showcases a production-ready authentication system with:
- User registration with password hashing (bcrypt)
- Login with JWT token generation
- Protected routes with authentication decorators
- Role-based access control (admin, author, reader)
- Token refresh mechanism
- User profile management
- Secure password handling

ARCHITECTURE:

Authentication Flow:
  Register → Hash Password → Store User
  Login → Verify Password → Generate JWT → Return Token
  Protected Route → Verify JWT → Extract User → Authorize → Process Request

DATABASE SCHEMA:

users_auth:
  - id, username, email, password_hash
  - role (admin, author, reader)
  - is_active, created_at, updated_at

posts_auth:
  - id, title, content, author_id
  - is_published, created_at, updated_at

token_blacklist_auth:
  - id, jti (JWT ID), created_at
  - Used for logout functionality
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
import os
import re
from dotenv import load_dotenv
import bcrypt

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ============================================================================
    # CONFIGURATION
    # ============================================================================

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables!")

    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Short-lived access token
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Longer-lived refresh token

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ============================================================================
    # EXTENSIONS
    # ============================================================================

    db = SQLAlchemy(app)
    jwt = JWTManager(app)

    # ============================================================================
    # API SETUP
    # ============================================================================

    api = Api(
        app,
        version='1.0',
        title='Secure Blog Platform API',
        description='Production-ready blog API with JWT authentication and role-based access control',
        doc='/swagger',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
            }
        },
        security='Bearer'
    )

    # ============================================================================
    # DATABASE MODELS
    # ============================================================================

    class User(db.Model):
        """
        User model with authentication fields.

        Security notes:
        - password_hash: NEVER store plain-text passwords!
        - role: Used for authorization (admin, author, reader)
        - is_active: Can disable user accounts
        """
        __tablename__ = 'users_auth'  # Chapter-specific table name

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)  # bcrypt hash
        role = db.Column(db.String(20), default='reader', nullable=False, index=True)  # reader, author, admin
        is_active = db.Column(db.Boolean, default=True, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Relationships
        posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

        def set_password(self, password):
            """Hash password with bcrypt before storing."""
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        def check_password(self, password):
            """Verify password against stored hash."""
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

        def to_dict(self, include_email=False):
            """Convert user to dictionary (never include password_hash!)"""
            result = {
                'id': self.id,
                'username': self.username,
                'role': self.role,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
            if include_email:
                result['email'] = self.email
            return result


    class Post(db.Model):
        """
        Post model with author relationship.

        Authorization rules:
        - Anyone can read published posts
        - Only authenticated authors can create posts
        - Authors can only edit/delete their own posts
        - Admins can edit/delete any post
        """
        __tablename__ = 'posts_auth'  # Chapter-specific table name

        id = db.Column(db.Integer, primary_key=True)
        author_id = db.Column(db.Integer, db.ForeignKey('users_auth.id'), nullable=False, index=True)
        title = db.Column(db.String(200), nullable=False)
        content = db.Column(db.Text, nullable=False)
        is_published = db.Column(db.Boolean, default=False, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def to_dict(self, include_author=True):
            result = {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'is_published': self.is_published,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
            if include_author and self.author:
                result['author'] = {
                    'id': self.author.id,
                    'username': self.author.username
                }
            return result


    class TokenBlacklist(db.Model):
        """
        Token blacklist for logout functionality.

        When a user logs out, we add their token's JTI (JWT ID) to this table.
        The @jwt_required decorator checks this table to revoke tokens.
        """
        __tablename__ = 'token_blacklist_auth'  # Chapter-specific table name

        id = db.Column(db.Integer, primary_key=True)
        jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        @staticmethod
        def is_blacklisted(jti):
            """Check if a token is blacklisted."""
            return TokenBlacklist.query.filter_by(jti=jti).first() is not None


    # ============================================================================
    # CREATE TABLES
    # ============================================================================

    with app.app_context():
        db.create_all()
        print("[OK] Database tables created successfully!")

    # ============================================================================
    # JWT CALLBACKS
    # ============================================================================

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """
        Callback to check if a token has been revoked (blacklisted).
        Called automatically by @jwt_required decorator.
        """
        jti = jwt_payload['jti']
        return TokenBlacklist.is_blacklisted(jti)

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================

    def validate_email(email):
        """Validate email format using regex."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def validate_password_strength(password):
        """
        Validate password meets security requirements.

        Requirements:
        - At least 8 characters
        - Contains at least one number
        - Contains at least one letter
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"

        if not re.search(r'[a-zA-Z]', password):
            return False, "Password must contain at least one letter"

        return True, None

    def require_role(*allowed_roles):
        """
        Decorator to require specific roles.

        Usage:
            @require_role('admin')
            def delete_user():
                ...

            @require_role('admin', 'author')
            def create_post():
                ...
        """
        def decorator(fn):
            @wraps(fn)
            @jwt_required()
            def wrapper(*args, **kwargs):
                user_id = get_jwt_identity()
                user = User.query.get(user_id)

                if not user:
                    return {'error': 'User not found'}, 404

                if not user.is_active:
                    return {'error': 'Account is disabled'}, 403

                if user.role not in allowed_roles:
                    return {'error': f'Requires one of these roles: {", ".join(allowed_roles)}'}, 403

                return fn(*args, **kwargs)
            return wrapper
        return decorator

    # ============================================================================
    # API MODELS (for Swagger)
    # ============================================================================

    auth_ns = Namespace('auth', description='Authentication operations')
    posts_ns = Namespace('posts', description='Blog post operations')
    admin_ns = Namespace('admin', description='Admin operations (requires admin role)')

    # Auth models
    register_model = auth_ns.model('Register', {
        'username': fields.String(required=True, description='Username', min_length=3, max_length=80, example='johndoe'),
        'email': fields.String(required=True, description='Email address', example='john@example.com'),
        'password': fields.String(required=True, description='Password (min 8 chars, must contain letter and number)', example='SecurePass123'),
        'role': fields.String(description='User role', enum=['reader', 'author', 'admin'], default='reader', example='author')
    })

    login_model = auth_ns.model('Login', {
        'email': fields.String(required=True, description='Email address', example='john@example.com'),
        'password': fields.String(required=True, description='Password', example='SecurePass123')
    })

    token_response_model = auth_ns.model('TokenResponse', {
        'access_token': fields.String(description='JWT access token'),
        'refresh_token': fields.String(description='JWT refresh token'),
        'token_type': fields.String(description='Token type', example='Bearer'),
        'expires_in': fields.Integer(description='Token expiration in seconds')
    })

    user_response_model = auth_ns.model('UserResponse', {
        'id': fields.Integer(description='User ID'),
        'username': fields.String(description='Username'),
        'email': fields.String(description='Email'),
        'role': fields.String(description='User role'),
        'is_active': fields.Boolean(description='Account status'),
        'created_at': fields.String(description='Registration date')
    })

    update_profile_model = auth_ns.model('UpdateProfile', {
        'username': fields.String(description='New username', example='johndoe'),
        'email': fields.String(description='New email', example='newemail@example.com')
    })

    change_password_model = auth_ns.model('ChangePassword', {
        'current_password': fields.String(required=True, description='Current password'),
        'new_password': fields.String(required=True, description='New password (min 8 chars)')
    })

    # Post models
    post_input_model = posts_ns.model('PostInput', {
        'title': fields.String(required=True, description='Post title', min_length=5, max_length=200, example='My First Blog Post'),
        'content': fields.String(required=True, description='Post content', example='This is the content of my blog post...'),
        'is_published': fields.Boolean(description='Publish immediately', default=False, example=True)
    })

    post_output_model = posts_ns.model('Post', {
        'id': fields.Integer(description='Post ID'),
        'title': fields.String(description='Title'),
        'content': fields.String(description='Content'),
        'is_published': fields.Boolean(description='Published status'),
        'author': fields.Nested(auth_ns.model('Author', {
            'id': fields.Integer(description='Author ID'),
            'username': fields.String(description='Author username')
        })),
        'created_at': fields.String(description='Created date'),
        'updated_at': fields.String(description='Updated date')
    })

    # ============================================================================
    # AUTHENTICATION ENDPOINTS
    # ============================================================================

    @auth_ns.route('/register')
    class Register(Resource):
        @auth_ns.doc('register_user')
        @auth_ns.expect(register_model, validate=True)
        @auth_ns.marshal_with(user_response_model, code=201)
        @auth_ns.response(400, 'Validation error')
        @auth_ns.response(409, 'User already exists')
        def post(self):
            """
            Register a new user account.

            This endpoint:
            1. Validates email format and password strength
            2. Checks for duplicate username/email
            3. Hashes the password with bcrypt
            4. Creates the user account
            5. Returns user information (NOT the password!)

            Security notes:
            - Password is hashed before storage (bcrypt with auto-salt)
            - Password is never returned in response
            - Email must be unique
            """
            data = request.json

            # Validate email format
            if not validate_email(data['email']):
                return {'error': 'Invalid email format'}, 400

            # Validate password strength
            is_valid, error_msg = validate_password_strength(data['password'])
            if not is_valid:
                return {'error': error_msg}, 400

            # Check for duplicate username
            if User.query.filter_by(username=data['username']).first():
                return {'error': 'Username already exists'}, 409

            # Check for duplicate email
            if User.query.filter_by(email=data['email']).first():
                return {'error': 'Email already exists'}, 409

            # Create new user
            user = User(
                username=data['username'],
                email=data['email'],
                role=data.get('role', 'reader')
            )
            user.set_password(data['password'])  # Hash the password

            db.session.add(user)
            db.session.commit()

            return user.to_dict(include_email=True), 201


    @auth_ns.route('/login')
    class Login(Resource):
        @auth_ns.doc('login_user')
        @auth_ns.expect(login_model, validate=True)
        @auth_ns.marshal_with(token_response_model)
        @auth_ns.response(401, 'Invalid credentials')
        def post(self):
            """
            Login and receive JWT tokens.

            This endpoint:
            1. Finds user by email
            2. Verifies password against stored hash
            3. Generates access token (short-lived, 1 hour)
            4. Generates refresh token (long-lived, 30 days)
            5. Returns both tokens

            How to use the token:
            - Include in Authorization header: "Bearer <access_token>"
            - When access token expires, use refresh token to get new one
            """
            data = request.json

            # Find user by email
            user = User.query.filter_by(email=data['email']).first()

            # Verify user exists and password is correct
            if not user or not user.check_password(data['password']):
                return {'error': 'Invalid email or password'}, 401

            # Check if account is active
            if not user.is_active:
                return {'error': 'Account is disabled'}, 403

            # Create tokens with user identity
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 3600  # 1 hour in seconds
            }, 200


    @auth_ns.route('/refresh')
    class RefreshToken(Resource):
        @auth_ns.doc('refresh_token', security='Bearer')
        @auth_ns.marshal_with(token_response_model)
        @auth_ns.response(401, 'Invalid or expired refresh token')
        @jwt_required(refresh=True)  # Requires refresh token, not access token
        def post(self):
            """
            Get a new access token using refresh token.

            When your access token expires (after 1 hour), use this endpoint
            to get a new one without requiring the user to login again.

            Send the refresh token (not access token) in Authorization header.
            """
            current_user_id = get_jwt_identity()

            # Generate new access token
            new_access_token = create_access_token(identity=current_user_id)

            return {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': 3600
            }, 200


    @auth_ns.route('/logout')
    class Logout(Resource):
        @auth_ns.doc('logout_user', security='Bearer')
        @auth_ns.response(200, 'Successfully logged out')
        @auth_ns.response(401, 'Missing or invalid token')
        @jwt_required()
        def post(self):
            """
            Logout by blacklisting the current token.

            This adds the token's JTI (JWT ID) to the blacklist.
            The token will be rejected on subsequent requests.

            Note: Client should also delete the token from local storage!
            """
            jti = get_jwt()['jti']  # Get JWT ID from current token

            # Add to blacklist
            blacklisted_token = TokenBlacklist(jti=jti)
            db.session.add(blacklisted_token)
            db.session.commit()

            return {'message': 'Successfully logged out'}, 200


    @auth_ns.route('/me')
    class CurrentUser(Resource):
        @auth_ns.doc('get_current_user', security='Bearer')
        @auth_ns.marshal_with(user_response_model)
        @auth_ns.response(401, 'Missing or invalid token')
        @jwt_required()
        def get(self):
            """
            Get current authenticated user's profile.

            This demonstrates how to get the user from a JWT token.
            The user_id is extracted from the token's identity claim.
            """
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {'error': 'User not found'}, 404

            return user.to_dict(include_email=True), 200

        @auth_ns.doc('update_current_user', security='Bearer')
        @auth_ns.expect(update_profile_model)
        @auth_ns.marshal_with(user_response_model)
        @auth_ns.response(409, 'Username or email already exists')
        def put(self):
            """
            Update current user's profile.

            Users can update their own username and email.
            Cannot change role (requires admin).
            """
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {'error': 'User not found'}, 404

            data = request.json

            # Check for duplicate username (if changing)
            if 'username' in data and data['username'] != user.username:
                if User.query.filter_by(username=data['username']).first():
                    return {'error': 'Username already exists'}, 409
                user.username = data['username']

            # Check for duplicate email (if changing)
            if 'email' in data and data['email'] != user.email:
                if not validate_email(data['email']):
                    return {'error': 'Invalid email format'}, 400
                if User.query.filter_by(email=data['email']).first():
                    return {'error': 'Email already exists'}, 409
                user.email = data['email']

            db.session.commit()
            return user.to_dict(include_email=True), 200


    @auth_ns.route('/me/password')
    class ChangePassword(Resource):
        @auth_ns.doc('change_password', security='Bearer')
        @auth_ns.expect(change_password_model, validate=True)
        @auth_ns.response(200, 'Password changed successfully')
        @auth_ns.response(400, 'Invalid current password or weak new password')
        @jwt_required()
        def put(self):
            """
            Change user's password.

            Requires current password for security.
            New password must meet strength requirements.
            """
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return {'error': 'User not found'}, 404

            data = request.json

            # Verify current password
            if not user.check_password(data['current_password']):
                return {'error': 'Current password is incorrect'}, 400

            # Validate new password strength
            is_valid, error_msg = validate_password_strength(data['new_password'])
            if not is_valid:
                return {'error': error_msg}, 400

            # Update password
            user.set_password(data['new_password'])
            db.session.commit()

            return {'message': 'Password changed successfully'}, 200


    # ============================================================================
    # POST ENDPOINTS (with authorization)
    # ============================================================================

    @posts_ns.route('/')
    class PostList(Resource):
        @posts_ns.doc('list_posts')
        @posts_ns.marshal_list_with(post_output_model)
        @posts_ns.param('published_only', 'Show only published posts', type='boolean', default=True)
        def get(self):
            """
            List all posts (public endpoint).

            By default, shows only published posts.
            Authenticated authors can see their own drafts.
            Admins can see all posts.
            """
            published_only = request.args.get('published_only', 'true').lower() == 'true'

            # Check if user is authenticated
            try:
                user_id = get_jwt_identity() if request.headers.get('Authorization') else None
                user = User.query.get(user_id) if user_id else None
            except:
                user = None

            # Build query based on user role
            if user and user.role == 'admin':
                # Admins see everything
                posts = Post.query.all()
            elif user:
                # Authenticated users see published posts + their own drafts
                if published_only:
                    posts = Post.query.filter(
                        (Post.is_published == True) | (Post.author_id == user.id)
                    ).all()
                else:
                    posts = Post.query.filter(Post.author_id == user.id).all()
            else:
                # Anonymous users see only published posts
                posts = Post.query.filter_by(is_published=True).all()

            return [post.to_dict() for post in posts], 200

        @posts_ns.doc('create_post', security='Bearer')
        @posts_ns.expect(post_input_model, validate=True)
        @posts_ns.marshal_with(post_output_model, code=201)
        @posts_ns.response(403, 'Requires author or admin role')
        @require_role('author', 'admin')
        def post(self):
            """
            Create a new blog post.

            Requires: author or admin role
            The authenticated user becomes the post's author.
            """
            user_id = get_jwt_identity()
            data = request.json

            post = Post(
                author_id=user_id,
                title=data['title'],
                content=data['content'],
                is_published=data.get('is_published', False)
            )

            db.session.add(post)
            db.session.commit()

            return post.to_dict(), 201


    @posts_ns.route('/<int:id>')
    @posts_ns.param('id', 'Post identifier')
    class PostItem(Resource):
        @posts_ns.doc('get_post')
        @posts_ns.marshal_with(post_output_model)
        @posts_ns.response(404, 'Post not found')
        def get(self, id):
            """
            Get a specific post (public endpoint).

            Published posts are public.
            Unpublished posts can only be viewed by author or admin.
            """
            post = Post.query.get_or_404(id)

            # Check if user is authenticated
            try:
                user_id = get_jwt_identity() if request.headers.get('Authorization') else None
                user = User.query.get(user_id) if user_id else None
            except:
                user = None

            # Check authorization
            if not post.is_published:
                if not user or (user.id != post.author_id and user.role != 'admin'):
                    return {'error': 'Post not found'}, 404

            return post.to_dict(), 200

        @posts_ns.doc('update_post', security='Bearer')
        @posts_ns.expect(post_input_model, validate=True)
        @posts_ns.marshal_with(post_output_model)
        @posts_ns.response(403, 'Not authorized to edit this post')
        @jwt_required()
        def put(self, id):
            """
            Update a post.

            Authors can update their own posts.
            Admins can update any post.
            """
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            post = Post.query.get_or_404(id)

            # Check authorization: must be author or admin
            if user.id != post.author_id and user.role != 'admin':
                return {'error': 'Not authorized to edit this post'}, 403

            data = request.json
            post.title = data['title']
            post.content = data['content']
            post.is_published = data.get('is_published', post.is_published)

            db.session.commit()
            return post.to_dict(), 200

        @posts_ns.doc('delete_post', security='Bearer')
        @posts_ns.response(204, 'Post deleted')
        @posts_ns.response(403, 'Not authorized to delete this post')
        @jwt_required()
        def delete(self, id):
            """
            Delete a post.

            Authors can delete their own posts.
            Admins can delete any post.
            """
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            post = Post.query.get_or_404(id)

            # Check authorization: must be author or admin
            if user.id != post.author_id and user.role != 'admin':
                return {'error': 'Not authorized to delete this post'}, 403

            db.session.delete(post)
            db.session.commit()
            return '', 204


    # ============================================================================
    # ADMIN ENDPOINTS (admin role required)
    # ============================================================================

    @admin_ns.route('/users')
    class AdminUserList(Resource):
        @admin_ns.doc('admin_list_users', security='Bearer')
        @admin_ns.marshal_list_with(user_response_model)
        @admin_ns.response(403, 'Requires admin role')
        @require_role('admin')
        def get(self):
            """
            List all users (admin only).

            Returns all users with their details.
            """
            users = User.query.all()
            return [user.to_dict(include_email=True) for user in users], 200


    @admin_ns.route('/users/<int:user_id>')
    @admin_ns.param('user_id', 'User identifier')
    class AdminUserItem(Resource):
        @admin_ns.doc('admin_delete_user', security='Bearer')
        @admin_ns.response(204, 'User deleted')
        @admin_ns.response(403, 'Requires admin role')
        @admin_ns.response(400, 'Cannot delete yourself')
        @require_role('admin')
        def delete(self, user_id):
            """
            Delete a user (admin only).

            Deletes user and all their posts (cascade).
            Cannot delete yourself.
            """
            current_user_id = get_jwt_identity()

            if current_user_id == user_id:
                return {'error': 'Cannot delete yourself'}, 400

            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()

            return '', 204

        @admin_ns.doc('admin_toggle_user_status', security='Bearer')
        @admin_ns.response(200, 'User status updated')
        @admin_ns.response(403, 'Requires admin role')
        @require_role('admin')
        def patch(self, user_id):
            """
            Toggle user active status (admin only).

            Disable/enable user accounts without deleting them.
            """
            user = User.query.get_or_404(user_id)
            user.is_active = not user.is_active
            db.session.commit()

            return {
                'id': user.id,
                'username': user.username,
                'is_active': user.is_active
            }, 200


    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(posts_ns, path='/posts')
    api.add_namespace(admin_ns, path='/admin')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*80)
    print("SECURE BLOG PLATFORM API - DEMO (Chapter 4: Authentication)")
    print("="*80)
    print("\n✨ FEATURES:")
    print("  ✅ User registration with bcrypt password hashing")
    print("  ✅ Login with JWT token generation")
    print("  ✅ Protected routes with @jwt_required and @require_role")
    print("  ✅ Role-based access control (reader, author, admin)")
    print("  ✅ Token refresh mechanism")
    print("  ✅ Logout with token blacklisting")
    print("  ✅ Secure password change")
    print("\n🚀 QUICK START:")
    print("  1. Register: POST /auth/register")
    print("  2. Login: POST /auth/login → Get JWT token")
    print("  3. Use token: Add header 'Authorization: Bearer <token>'")
    print("  4. Create post: POST /posts (requires author role)")
    print("  5. View profile: GET /auth/me")
    print("\n📚 LEARNING HIGHLIGHTS:")
    print("  - Password hashing: bcrypt with auto-salt")
    print("  - JWT tokens: Stateless authentication")
    print("  - Authorization: Role-based access control")
    print("  - Security: Token blacklist, password validation")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("   (Use 'Authorize' button to add JWT token)")
    print("="*80 + "\n")

    app.run(debug=True, port=5000)
