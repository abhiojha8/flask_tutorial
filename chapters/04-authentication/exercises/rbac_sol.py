"""
Exercise 4: Role-Based Access Control (RBAC)
Complete solution with custom @require_role decorator

CONCEPTS:
- Adding 'role' field to User model
- Creating custom decorator for role checking
- Protecting endpoints based on user role
- Different permissions for different roles
"""

from flask import Flask, request
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import (
    JWTManager, create_access_token, 
    jwt_required, get_jwt_identity
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import os
import re
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# APP SETUP
# ============================================================================

app = Flask(__name__)
CORS(app)

database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL not found!")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(
    app,
    version='1.0',
    title='Exercise 4: RBAC',
    description='Role-Based Access Control Demo',
    doc='/swagger'
)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    """User model with role field for RBAC"""
    __tablename__ = 'users_rbac'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        default='reader',
        index=True
    )  # 'reader', 'author', 'admin'
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to posts
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_password(self, password):
        """Hash password with bcrypt"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self):
        """Convert to dictionary (NEVER include password!)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Post(db.Model):
    """Post model owned by users"""
    __tablename__ = 'posts_rbac'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users_rbac.id'),
        nullable=False,
        index=True
    )
    status = db.Column(db.String(20), default='draft')  # draft, published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_author=False):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_author and self.author:
            result['author'] = self.author.to_dict()
        return result


# Create tables
with app.app_context():
    db.create_all()
    print("[✓] Database tables created!")

# ============================================================================
# CUSTOM DECORATOR: require_role
# ============================================================================

def require_role(*allowed_roles):
    """
    Custom decorator to protect endpoints based on user role.

    Usage:
        @require_role('author', 'admin')
        def create_post(self):
            # Only users with 'author' or 'admin' role can access
            pass

    Flow:
    1. Extract JWT token (requires @jwt_required())
    2. Get user_id from token
    3. Fetch user from database
    4. Check if user.role is in allowed_roles
    5. If yes → execute endpoint
    6. If no → return 403 Forbidden
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()  # Must have valid JWT token
        def wrapper(*args, **kwargs):
            # Step 1: Get user ID from JWT token
            user_id = get_jwt_identity()

            # Step 2: Fetch user from database
            user = User.query.get(user_id)

            # Step 3: User not found
            if not user:
                return {'error': 'User not found'}, 404

            # Step 4: User account is disabled
            if not user.is_active:
                return {'error': 'Account is disabled'}, 403

            # Step 5: Check if user role is allowed
            if user.role not in allowed_roles:
                return {
                    'error': f'Requires one of these roles: {", ".join(allowed_roles)}',
                    'your_role': user.role
                }, 403

            # Step 6: All checks passed - execute the endpoint
            return fn(*args, **kwargs)

        return wrapper

    return decorator

# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
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

auth_ns = Namespace('auth', description='Authentication')
posts_ns = Namespace('posts', description='Posts (with RBAC)')
admin_ns = Namespace('admin', description='Admin only')

# Auth models
register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, example='johndoe'),
    'email': fields.String(required=True, example='john@example.com'),
    'password': fields.String(required=True, example='password123'),
    'role': fields.String(description='User role', enum=['reader', 'author', 'admin'], example='reader')
})

login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, example='john@example.com'),
    'password': fields.String(required=True, example='password123')
})

user_model = auth_ns.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email'),
    'role': fields.String(description='User role'),
    'is_active': fields.Boolean(description='Active status'),
    'created_at': fields.String(description='Created timestamp')
})

token_model = auth_ns.model('Token', {
    'access_token': fields.String(description='JWT access token'),
    'token_type': fields.String(example='Bearer'),
    'expires_in': fields.Integer(example=3600)
})

# Post models
post_input_model = posts_ns.model('PostInput', {
    'title': fields.String(required=True, example='My First Post'),
    'content': fields.String(required=True, example='Post content here'),
    'status': fields.String(enum=['draft', 'published'], example='draft')
})

post_model = posts_ns.model('Post', {
    'id': fields.Integer(description='Post ID'),
    'title': fields.String(description='Title'),
    'content': fields.String(description='Content'),
    'user_id': fields.Integer(description='Author ID'),
    'status': fields.String(description='Status'),
    'created_at': fields.String(description='Created timestamp'),
    'updated_at': fields.String(description='Updated timestamp')
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
        Register new user with optional role.
        
        Roles:
        - 'reader': Can only read posts
        - 'author': Can create and edit their own posts
        - 'admin': Full access
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
            email=data['email'],
            role=data.get('role', 'reader')  # Default to 'reader'
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return user.to_dict(), 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.marshal_with(token_model)
    def post(self):
        """Login and get JWT token"""
        data = request.json

        # Find user
        user = User.query.filter_by(email=data['email']).first()

        # Verify credentials
        if not user or not user.check_password(data['password']):
            return {'error': 'Invalid email or password'}, 401

        # Create JWT token
        access_token = create_access_token(identity=user.id)

        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }, 200


@auth_ns.route('/me')
class Profile(Resource):
    @auth_ns.marshal_with(user_model)
    @jwt_required()
    def get(self):
        """Get current user profile"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        return user.to_dict(), 200

# ============================================================================
# POST ENDPOINTS WITH RBAC
# ============================================================================

@posts_ns.route('/')
class PostList(Resource):
    @posts_ns.marshal_list_with(post_model)
    def get(self):
        """List all published posts (everyone can read)"""
        posts = Post.query.filter_by(status='published').all()
        return [post.to_dict() for post in posts], 200

    @require_role('author', 'admin')  # ← RBAC: Only authors and admins
    @posts_ns.expect(post_input_model)
    @posts_ns.marshal_with(post_model, code=201)
    def post(self):
        """
        Create new post.

        RBAC: Only users with 'author' or 'admin' role can create posts.
        Readers will get 403 Forbidden.
        """
        user_id = get_jwt_identity()
        data = request.json

        post = Post(
            title=data['title'],
            content=data['content'],
            status=data.get('status', 'draft'),
            user_id=user_id
        )

        db.session.add(post)
        db.session.commit()

        return post.to_dict(), 201


@posts_ns.route('/<int:post_id>')
class PostDetail(Resource):
    @posts_ns.marshal_with(post_model)
    def get(self, post_id):
        """Get single post (everyone can read published posts)"""
        post = Post.query.get(post_id)

        if not post:
            return {'error': 'Post not found'}, 404

        if post.status != 'published':
            return {'error': 'Post not available'}, 403

        return post.to_dict(), 200

    @require_role('author', 'admin')  # ← RBAC: Must be author or admin
    @posts_ns.expect(post_input_model)
    @posts_ns.marshal_with(post_model)
    def put(self, post_id):
        """
        Update post.

        RBAC: Only authors (if they own the post) or admins can edit.
        """
        user_id = get_jwt_identity()
        post = Post.query.get(post_id)

        if not post:
            return {'error': 'Post not found'}, 404

        # Authorization: Check if user is owner or admin
        user = User.query.get(user_id)
        if post.user_id != user_id and user.role != 'admin':
            return {'error': 'You can only edit your own posts'}, 403

        data = request.json
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.status = data.get('status', post.status)

        db.session.commit()

        return post.to_dict(), 200

    @require_role('author', 'admin')  # ← RBAC: Must be author or admin
    def delete(self, post_id):
        """
        Delete post.

        RBAC: Only authors (if they own) or admins can delete.
        """
        user_id = get_jwt_identity()
        post = Post.query.get(post_id)

        if not post:
            return {'error': 'Post not found'}, 404

        # Authorization: Check if user is owner or admin
        user = User.query.get(user_id)
        if post.user_id != user_id and user.role != 'admin':
            return {'error': 'You can only delete your own posts'}, 403

        db.session.delete(post)
        db.session.commit()

        return {'message': 'Post deleted'}, 200


# ============================================================================
# ADMIN-ONLY ENDPOINTS
# ============================================================================

@admin_ns.route('/users')
class AdminUsers(Resource):
    @require_role('admin')  # ← RBAC: ONLY admins
    @admin_ns.marshal_list_with(user_model)
    def get(self):
        """List all users (admin only)"""
        users = User.query.all()
        return [user.to_dict() for user in users], 200


@admin_ns.route('/users/<int:user_id>/role')
class AdminChangeRole(Resource):
    @require_role('admin')  # ← RBAC: ONLY admins
    def put(self, user_id):
        """
        Change user role (admin only).

        Body: {"role": "author"}
        """
        user = User.query.get(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        data = request.json
        new_role = data.get('role')

        if new_role not in ['reader', 'author', 'admin']:
            return {'error': 'Invalid role'}, 400

        user.role = new_role
        db.session.commit()

        return user.to_dict(), 200

# ============================================================================
# REGISTER NAMESPACES
# ============================================================================

api.add_namespace(auth_ns, path='/api/auth')
api.add_namespace(posts_ns, path='/api/posts')
api.add_namespace(admin_ns, path='/api/admin')

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("EXERCISE 4: ROLE-BASED ACCESS CONTROL (RBAC)")
    print("="*70)
    print("\n📋 USER ROLES:")
    print("  • reader   : Can only read published posts")
    print("  • author   : Can create and edit their own posts")
    print("  • admin    : Full access to everything")
    print("\n🚀 TEST SCENARIOS:")
    print("\n1️⃣  Register as READER:")
    print("   POST /api/auth/register")
    print("   {\"username\": \"reader1\", \"email\": \"reader@ex.com\",")
    print("    \"password\": \"Pass123\", \"role\": \"reader\"}")
    print("\n2️⃣  Register as AUTHOR:")
    print("   POST /api/auth/register")
    print("   {\"username\": \"author1\", \"email\": \"author@ex.com\",")
    print("    \"password\": \"Pass123\", \"role\": \"author\"}")
    print("\n3️⃣  Register as ADMIN:")
    print("   POST /api/auth/register")
    print("   {\"username\": \"admin1\", \"email\": \"admin@ex.com\",")
    print("    \"password\": \"Pass123\", \"role\": \"admin\"}")
    print("\n4️⃣  LOGIN and copy token:")
    print("   POST /api/auth/login")
    print("   {\"email\": \"reader@ex.com\", \"password\": \"Pass123\"}")
    print("\n5️⃣  TRY TO CREATE POST as READER (should FAIL - 403):")
    print("   POST /api/posts/")
    print("   Authorization: Bearer <reader_token>")
    print("   {\"title\": \"My Post\", \"content\": \"...\", \"status\": \"draft\"}")
    print("\n6️⃣  CREATE POST as AUTHOR (should SUCCESS - 201):")
    print("   POST /api/posts/")
    print("   Authorization: Bearer <author_token>")
    print("   {\"title\": \"My Post\", \"content\": \"...\", \"status\": \"draft\"}")
    print("\n7️⃣  VIEW ALL USERS as ADMIN (should SUCCESS):")
    print("   GET /api/admin/users")
    print("   Authorization: Bearer <admin_token>")
    print("\n8️⃣  CHANGE USER ROLE as ADMIN:")
    print("   PUT /api/admin/users/1/role")
    print("   Authorization: Bearer <admin_token>")
    print("   {\"role\": \"author\"}")
    print("\n📚 KEY CONCEPTS:")
    print("  ✅ Custom @require_role() decorator")
    print("  ✅ Multiple roles per endpoint")
    print("  ✅ User authorization (owner can edit own posts)")
    print("  ✅ Admin-only endpoints")
    print("  ✅ 403 Forbidden for insufficient permissions")
    print("\n🌐 API Docs: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)