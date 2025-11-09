"""
DEMO: Multi-tenant Blog Platform API
Chapter 3: Database Integration with PostgreSQL & Supabase

This demo showcases a production-ready blog platform with:
- Multi-tenant architecture (organizations)
- Complete database relationships
- Audit logging for compliance
- Soft deletes with restore capability
- Query optimization (indexes, eager loading)
- Proper error handling
- Swagger documentation

ARCHITECTURE:

Organizations (Tenants)
    ├── Users
    │   └── Posts
    └── Posts

AuditLogs (tracks all changes)

DATABASE SCHEMA:

organizations:
  - id, name, slug, plan, is_active, created_at, updated_at, deleted_at

users:
  - id, username, email, full_name, is_active
  - organization_id (FK → organizations)
  - created_at, updated_at, deleted_at

posts:
  - id, title, content, status, view_count
  - user_id (FK → users)
  - organization_id (FK → organizations)
  - created_at, updated_at, deleted_at

audit_logs:
  - id, user_id, action, table_name, record_id
  - old_values (JSON), new_values (JSON)
  - ip_address, created_at
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload
from sqlalchemy import Index
from sqlalchemy.exc import IntegrityError

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

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Enable SQL logging for learning (disable in production)
    # app.config['SQLALCHEMY_ECHO'] = True

    # ============================================================================
    # API SETUP
    # ============================================================================

    api = Api(
        app,
        version='1.0',
        title='Multi-tenant Blog Platform API',
        description='Production-ready blog platform with multi-tenancy, audit logging, and soft deletes',
        doc='/swagger'
    )

    # ============================================================================
    # DATABASE
    # ============================================================================

    db = SQLAlchemy(app)

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================

    def log_audit(user_id, action, table_name, record_id, old_values=None, new_values=None):
        """
        Create an audit log entry.

        In a real app, user_id would come from authentication.
        """
        try:
            ip_address = request.remote_addr if request else None

            audit = AuditLog(
                user_id=user_id,
                action=action,
                table_name=table_name,
                record_id=record_id,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                ip_address=ip_address,
                created_at=datetime.utcnow()
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            print(f"Audit logging failed: {e}")
            # Don't fail the main operation if audit fails
            db.session.rollback()

    # ============================================================================
    # MODELS
    # ============================================================================

    class Organization(db.Model):
        """
        Organization model representing a tenant.

        Indexes:
        - name: Fast lookups by organization name
        - slug: Fast lookups by URL slug
        - (is_active, plan): Fast filtering by active orgs and plan type
        """
        __tablename__ = 'organizations'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False, index=True)
        slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
        plan = db.Column(db.String(20), default='free', index=True)  # free, pro, enterprise
        is_active = db.Column(db.Boolean, default=True, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        deleted_at = db.Column(db.DateTime, nullable=True, index=True)

        # Relationships
        users = db.relationship('User', backref='organization', lazy=True)
        posts = db.relationship('Post', backref='organization', lazy=True)

        # Composite index for common query pattern
        __table_args__ = (
            Index('idx_org_active_plan', 'is_active', 'plan'),
        )

        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'slug': self.slug,
                'plan': self.plan,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
            }


    class User(db.Model):
        """
        User model belonging to an organization.

        Indexes:
        - username: Unique constraint + fast lookups
        - email: Unique constraint + fast lookups
        - organization_id: Fast filtering by org
        - (organization_id, is_active): Fast queries for active users in org
        """
        __tablename__ = 'users'

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False, index=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        full_name = db.Column(db.String(100), nullable=True)
        is_active = db.Column(db.Boolean, default=True, index=True)
        organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        deleted_at = db.Column(db.DateTime, nullable=True, index=True)

        # Relationships
        posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

        # Composite index
        __table_args__ = (
            Index('idx_user_org_active', 'organization_id', 'is_active'),
        )

        def to_dict(self, include_organization=False):
            result = {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'is_active': self.is_active,
                'organization_id': self.organization_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
            }
            if include_organization and self.organization:
                result['organization'] = self.organization.to_dict()
            return result


    class Post(db.Model):
        """
        Post model belonging to a user and organization.

        Indexes:
        - user_id: Fast filtering by author
        - organization_id: Fast filtering by org
        - status: Fast filtering by status
        - (organization_id, status): Fast queries for published posts in org
        - (organization_id, created_at): Fast queries for recent posts in org
        """
        __tablename__ = 'posts'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)
        title = db.Column(db.String(200), nullable=False)
        content = db.Column(db.Text, nullable=True)
        status = db.Column(db.String(20), default='draft', index=True)  # draft, published, archived
        view_count = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        deleted_at = db.Column(db.DateTime, nullable=True, index=True)

        # Composite indexes
        __table_args__ = (
            Index('idx_post_org_status', 'organization_id', 'status'),
            Index('idx_post_org_created', 'organization_id', 'created_at'),
        )

        def to_dict(self, include_author=False, include_organization=False):
            result = {
                'id': self.id,
                'user_id': self.user_id,
                'organization_id': self.organization_id,
                'title': self.title,
                'content': self.content,
                'status': self.status,
                'view_count': self.view_count,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
            }
            if include_author and self.author:
                result['author'] = self.author.to_dict()
            if include_organization and self.organization:
                result['organization'] = self.organization.to_dict()
            return result


    class AuditLog(db.Model):
        """
        Audit log for tracking all data changes.

        Indexes:
        - action: Fast filtering by action type
        - table_name: Fast filtering by table
        - record_id: Fast filtering by record
        - (table_name, record_id): Fast queries for specific record history
        """
        __tablename__ = 'audit_logs'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
        action = db.Column(db.String(50), nullable=False, index=True)  # create, update, delete
        table_name = db.Column(db.String(50), nullable=False, index=True)
        record_id = db.Column(db.Integer, nullable=False, index=True)
        old_values = db.Column(db.Text, nullable=True)  # JSON string
        new_values = db.Column(db.Text, nullable=True)  # JSON string
        ip_address = db.Column(db.String(45), nullable=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

        # Composite index
        __table_args__ = (
            Index('idx_audit_table_record', 'table_name', 'record_id'),
        )

        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'action': self.action,
                'table_name': self.table_name,
                'record_id': self.record_id,
                'old_values': json.loads(self.old_values) if self.old_values else None,
                'new_values': json.loads(self.new_values) if self.new_values else None,
                'ip_address': self.ip_address,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    # ============================================================================
    # CREATE TABLES
    # ============================================================================

    with app.app_context():
        db.create_all()
        print("[OK] Database tables created successfully with all indexes!")

    # ============================================================================
    # API MODELS (for Swagger)
    # ============================================================================

    orgs_ns = Namespace('organizations', description='Organization management')
    users_ns = Namespace('users', description='User operations')
    posts_ns = Namespace('posts', description='Post operations')
    audit_ns = Namespace('audit-logs', description='Audit log operations')

    # Organization models
    org_input_model = orgs_ns.model('OrganizationInput', {
        'name': fields.String(required=True, description='Organization name', example='Acme Corporation'),
        'slug': fields.String(required=True, description='URL-friendly identifier', example='acme-corp'),
        'plan': fields.String(description='Plan type', enum=['free', 'pro', 'enterprise'], example='pro'),
        'is_active': fields.Boolean(description='Active status', example=True)
    })

    org_output_model = orgs_ns.model('Organization', {
        'id': fields.Integer(description='Organization ID'),
        'name': fields.String(description='Name'),
        'slug': fields.String(description='Slug'),
        'plan': fields.String(description='Plan'),
        'is_active': fields.Boolean(description='Active'),
        'created_at': fields.String(description='Created timestamp'),
        'updated_at': fields.String(description='Updated timestamp'),
        'deleted_at': fields.String(description='Deleted timestamp')
    })

    # User models
    user_input_model = users_ns.model('UserInput', {
        'username': fields.String(required=True, description='Unique username', example='johndoe'),
        'email': fields.String(required=True, description='Email address', example='john@example.com'),
        'full_name': fields.String(description='Full name', example='John Doe'),
        'organization_id': fields.Integer(required=True, description='Organization ID', example=1),
        'is_active': fields.Boolean(description='Active status', example=True)
    })

    user_output_model = users_ns.model('User', {
        'id': fields.Integer(description='User ID'),
        'username': fields.String(description='Username'),
        'email': fields.String(description='Email'),
        'full_name': fields.String(description='Full name'),
        'is_active': fields.Boolean(description='Active'),
        'organization_id': fields.Integer(description='Organization ID'),
        'created_at': fields.String(description='Created timestamp'),
        'updated_at': fields.String(description='Updated timestamp'),
        'deleted_at': fields.String(description='Deleted timestamp')
    })

    # Post models
    post_input_model = posts_ns.model('PostInput', {
        'user_id': fields.Integer(required=True, description='Author user ID', example=1),
        'organization_id': fields.Integer(required=True, description='Organization ID', example=1),
        'title': fields.String(required=True, description='Post title', example='My First Blog Post'),
        'content': fields.String(description='Post content', example='This is the content...'),
        'status': fields.String(description='Status', enum=['draft', 'published', 'archived'], example='draft')
    })

    post_output_model = posts_ns.model('Post', {
        'id': fields.Integer(description='Post ID'),
        'user_id': fields.Integer(description='Author ID'),
        'organization_id': fields.Integer(description='Organization ID'),
        'title': fields.String(description='Title'),
        'content': fields.String(description='Content'),
        'status': fields.String(description='Status'),
        'view_count': fields.Integer(description='View count'),
        'created_at': fields.String(description='Created'),
        'updated_at': fields.String(description='Updated'),
        'deleted_at': fields.String(description='Deleted'),
        'author': fields.Nested(user_output_model, skip_none=True)
    })

    # Audit log model
    audit_output_model = audit_ns.model('AuditLog', {
        'id': fields.Integer(description='Audit ID'),
        'user_id': fields.Integer(description='User who made change'),
        'action': fields.String(description='Action'),
        'table_name': fields.String(description='Table'),
        'record_id': fields.Integer(description='Record ID'),
        'old_values': fields.Raw(description='Old values'),
        'new_values': fields.Raw(description='New values'),
        'ip_address': fields.String(description='IP address'),
        'created_at': fields.String(description='Timestamp')
    })

    # ============================================================================
    # ORGANIZATION ENDPOINTS
    # ============================================================================

    @orgs_ns.route('/')
    class OrganizationList(Resource):
        @orgs_ns.doc('list_organizations')
        @orgs_ns.marshal_list_with(org_output_model)
        def get(self):
            """List all active organizations"""
            orgs = Organization.query.filter(Organization.deleted_at.is_(None)).all()
            return [org.to_dict() for org in orgs]

        @orgs_ns.doc('create_organization')
        @orgs_ns.expect(org_input_model)
        @orgs_ns.marshal_with(org_output_model, code=201)
        @orgs_ns.response(409, 'Organization already exists')
        def post(self):
            """Create a new organization"""
            data = request.json

            # Check for duplicates
            if Organization.query.filter_by(name=data['name']).first():
                return {'message': 'Organization with this name already exists'}, 409
            if Organization.query.filter_by(slug=data['slug']).first():
                return {'message': 'Organization with this slug already exists'}, 409

            try:
                org = Organization(
                    name=data['name'],
                    slug=data['slug'],
                    plan=data.get('plan', 'free'),
                    is_active=data.get('is_active', True)
                )
                db.session.add(org)
                db.session.commit()

                # Audit log
                log_audit(None, 'create', 'organizations', org.id, new_values=org.to_dict())

                return org.to_dict(), 201
            except IntegrityError:
                db.session.rollback()
                return {'message': 'Database integrity error'}, 409

    @orgs_ns.route('/<int:id>')
    @orgs_ns.param('id', 'Organization identifier')
    class OrganizationItem(Resource):
        @orgs_ns.doc('get_organization')
        @orgs_ns.marshal_with(org_output_model)
        @orgs_ns.response(404, 'Organization not found')
        def get(self, id):
            """Get organization by ID"""
            org = Organization.query.get_or_404(id)
            if org.deleted_at:
                return {'message': 'Organization not found'}, 404
            return org.to_dict()

        @orgs_ns.doc('delete_organization')
        @orgs_ns.response(204, 'Organization deleted')
        @orgs_ns.response(404, 'Organization not found')
        def delete(self, id):
            """Soft delete organization"""
            org = Organization.query.get_or_404(id)
            if org.deleted_at:
                return {'message': 'Organization not found'}, 404

            old_values = org.to_dict()
            org.deleted_at = datetime.utcnow()
            db.session.commit()

            log_audit(None, 'delete', 'organizations', id, old_values=old_values)
            return '', 204

    @orgs_ns.route('/<int:id>/users')
    @orgs_ns.param('id', 'Organization identifier')
    class OrganizationUsers(Resource):
        @orgs_ns.doc('get_organization_users')
        @orgs_ns.marshal_list_with(user_output_model)
        def get(self, id):
            """Get all users in organization"""
            org = Organization.query.get_or_404(id)
            users = User.query.filter_by(organization_id=id).filter(User.deleted_at.is_(None)).all()
            return [user.to_dict() for user in users]

    @orgs_ns.route('/<int:id>/posts')
    @orgs_ns.param('id', 'Organization identifier')
    class OrganizationPosts(Resource):
        @orgs_ns.doc('get_organization_posts')
        @orgs_ns.marshal_list_with(post_output_model)
        def get(self, id):
            """Get all posts in organization (with eager loaded authors)"""
            org = Organization.query.get_or_404(id)
            # Use eager loading to prevent N+1 queries
            posts = Post.query.filter_by(organization_id=id)\
                              .filter(Post.deleted_at.is_(None))\
                              .options(joinedload(Post.author))\
                              .all()
            return [post.to_dict(include_author=True) for post in posts]

    # ============================================================================
    # USER ENDPOINTS
    # ============================================================================

    @users_ns.route('/')
    class UserList(Resource):
        @users_ns.doc('list_users')
        @users_ns.marshal_list_with(user_output_model)
        def get(self):
            """List all active users"""
            users = User.query.filter(User.deleted_at.is_(None)).all()
            return [user.to_dict() for user in users]

        @users_ns.doc('create_user')
        @users_ns.expect(user_input_model)
        @users_ns.marshal_with(user_output_model, code=201)
        @users_ns.response(400, 'Validation Error')
        @users_ns.response(404, 'Organization not found')
        @users_ns.response(409, 'User already exists')
        def post(self):
            """Create a new user"""
            data = request.json

            # Validate organization exists
            org = Organization.query.get(data['organization_id'])
            if not org or org.deleted_at:
                return {'message': 'Organization not found'}, 404

            # Check for duplicates
            if User.query.filter_by(username=data['username']).first():
                return {'message': 'Username already exists'}, 409
            if User.query.filter_by(email=data['email']).first():
                return {'message': 'Email already exists'}, 409

            try:
                user = User(
                    username=data['username'],
                    email=data['email'],
                    full_name=data.get('full_name'),
                    organization_id=data['organization_id'],
                    is_active=data.get('is_active', True)
                )
                db.session.add(user)
                db.session.commit()

                log_audit(None, 'create', 'users', user.id, new_values=user.to_dict())
                return user.to_dict(), 201
            except IntegrityError:
                db.session.rollback()
                return {'message': 'Database integrity error'}, 409

    @users_ns.route('/<int:id>')
    @users_ns.param('id', 'User identifier')
    class UserItem(Resource):
        @users_ns.doc('get_user')
        @users_ns.marshal_with(user_output_model)
        @users_ns.response(404, 'User not found')
        def get(self, id):
            """Get user by ID"""
            user = User.query.get_or_404(id)
            if user.deleted_at:
                return {'message': 'User not found'}, 404
            return user.to_dict()

        @users_ns.doc('update_user')
        @users_ns.expect(user_input_model)
        @users_ns.marshal_with(user_output_model)
        @users_ns.response(404, 'User not found')
        @users_ns.response(409, 'Duplicate username/email')
        def put(self, id):
            """Update user"""
            user = User.query.get_or_404(id)
            if user.deleted_at:
                return {'message': 'User not found'}, 404

            data = request.json
            old_values = user.to_dict()

            # Check for duplicates (excluding current user)
            if 'username' in data:
                existing = User.query.filter_by(username=data['username']).first()
                if existing and existing.id != id:
                    return {'message': 'Username already exists'}, 409
                user.username = data['username']

            if 'email' in data:
                existing = User.query.filter_by(email=data['email']).first()
                if existing and existing.id != id:
                    return {'message': 'Email already exists'}, 409
                user.email = data['email']

            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'is_active' in data:
                user.is_active = data['is_active']

            db.session.commit()

            log_audit(None, 'update', 'users', id, old_values=old_values, new_values=user.to_dict())
            return user.to_dict()

        @users_ns.doc('delete_user')
        @users_ns.response(204, 'User deleted')
        @users_ns.response(404, 'User not found')
        def delete(self, id):
            """Soft delete user"""
            user = User.query.get_or_404(id)
            if user.deleted_at:
                return {'message': 'User not found'}, 404

            old_values = user.to_dict()
            user.deleted_at = datetime.utcnow()
            db.session.commit()

            log_audit(None, 'delete', 'users', id, old_values=old_values)
            return '', 204

    @users_ns.route('/<int:id>/restore')
    @users_ns.param('id', 'User identifier')
    class UserRestore(Resource):
        @users_ns.doc('restore_user')
        @users_ns.marshal_with(user_output_model)
        @users_ns.response(404, 'User not found or not deleted')
        def post(self, id):
            """Restore soft-deleted user"""
            user = User.query.get_or_404(id)
            if not user.deleted_at:
                return {'message': 'User is not deleted'}, 404

            user.deleted_at = None
            db.session.commit()

            log_audit(None, 'restore', 'users', id, new_values=user.to_dict())
            return user.to_dict()

    @users_ns.route('/<int:id>/posts')
    @users_ns.param('id', 'User identifier')
    class UserPosts(Resource):
        @users_ns.doc('get_user_posts')
        @users_ns.marshal_list_with(post_output_model)
        def get(self, id):
            """Get all posts by user"""
            user = User.query.get_or_404(id)
            posts = Post.query.filter_by(user_id=id).filter(Post.deleted_at.is_(None)).all()
            return [post.to_dict() for post in posts]

    # ============================================================================
    # POST ENDPOINTS
    # ============================================================================

    @posts_ns.route('/')
    class PostList(Resource):
        @posts_ns.doc('list_posts')
        @posts_ns.marshal_list_with(post_output_model)
        def get(self):
            """List all active posts (with eager loaded authors - no N+1!)"""
            posts = Post.query.filter(Post.deleted_at.is_(None))\
                              .options(joinedload(Post.author))\
                              .all()
            return [post.to_dict(include_author=True) for post in posts]

        @posts_ns.doc('create_post')
        @posts_ns.expect(post_input_model)
        @posts_ns.marshal_with(post_output_model, code=201)
        @posts_ns.response(404, 'User or organization not found')
        def post(self):
            """Create a new post"""
            data = request.json

            # Validate user exists
            user = User.query.get(data['user_id'])
            if not user or user.deleted_at:
                return {'message': 'User not found'}, 404

            # Validate organization exists
            org = Organization.query.get(data['organization_id'])
            if not org or org.deleted_at:
                return {'message': 'Organization not found'}, 404

            # Validate user belongs to organization
            if user.organization_id != data['organization_id']:
                return {'message': 'User does not belong to this organization'}, 400

            post = Post(
                user_id=data['user_id'],
                organization_id=data['organization_id'],
                title=data['title'],
                content=data.get('content'),
                status=data.get('status', 'draft')
            )
            db.session.add(post)
            db.session.commit()

            log_audit(data['user_id'], 'create', 'posts', post.id, new_values=post.to_dict())
            return post.to_dict(include_author=True), 201

    @posts_ns.route('/<int:id>')
    @posts_ns.param('id', 'Post identifier')
    class PostItem(Resource):
        @posts_ns.doc('get_post')
        @posts_ns.marshal_with(post_output_model)
        @posts_ns.response(404, 'Post not found')
        def get(self, id):
            """Get post by ID (with author info)"""
            post = Post.query.options(joinedload(Post.author)).get_or_404(id)
            if post.deleted_at:
                return {'message': 'Post not found'}, 404

            # Increment view count
            post.view_count += 1
            db.session.commit()

            return post.to_dict(include_author=True)

        @posts_ns.doc('update_post')
        @posts_ns.expect(post_input_model)
        @posts_ns.marshal_with(post_output_model)
        @posts_ns.response(404, 'Post not found')
        def put(self, id):
            """Update post"""
            post = Post.query.get_or_404(id)
            if post.deleted_at:
                return {'message': 'Post not found'}, 404

            data = request.json
            old_values = post.to_dict()

            if 'title' in data:
                post.title = data['title']
            if 'content' in data:
                post.content = data['content']
            if 'status' in data:
                post.status = data['status']

            db.session.commit()

            log_audit(post.user_id, 'update', 'posts', id, old_values=old_values, new_values=post.to_dict())
            return post.to_dict(include_author=True)

        @posts_ns.doc('delete_post')
        @posts_ns.response(204, 'Post deleted')
        @posts_ns.response(404, 'Post not found')
        def delete(self, id):
            """Soft delete post"""
            post = Post.query.get_or_404(id)
            if post.deleted_at:
                return {'message': 'Post not found'}, 404

            old_values = post.to_dict()
            post.deleted_at = datetime.utcnow()
            db.session.commit()

            log_audit(post.user_id, 'delete', 'posts', id, old_values=old_values)
            return '', 204

    @posts_ns.route('/<int:id>/restore')
    @posts_ns.param('id', 'Post identifier')
    class PostRestore(Resource):
        @posts_ns.doc('restore_post')
        @posts_ns.marshal_with(post_output_model)
        @posts_ns.response(404, 'Post not found or not deleted')
        def post(self, id):
            """Restore soft-deleted post"""
            post = Post.query.get_or_404(id)
            if not post.deleted_at:
                return {'message': 'Post is not deleted'}, 404

            post.deleted_at = None
            db.session.commit()

            log_audit(post.user_id, 'restore', 'posts', id, new_values=post.to_dict())
            return post.to_dict(include_author=True)

    # ============================================================================
    # AUDIT LOG ENDPOINTS
    # ============================================================================

    @audit_ns.route('/')
    class AuditLogList(Resource):
        @audit_ns.doc('list_audit_logs')
        @audit_ns.marshal_list_with(audit_output_model)
        @audit_ns.param('table_name', 'Filter by table name')
        @audit_ns.param('record_id', 'Filter by record ID')
        @audit_ns.param('action', 'Filter by action (create/update/delete)')
        def get(self):
            """List audit logs with optional filters"""
            query = AuditLog.query

            if 'table_name' in request.args:
                query = query.filter_by(table_name=request.args['table_name'])
            if 'record_id' in request.args:
                query = query.filter_by(record_id=int(request.args['record_id']))
            if 'action' in request.args:
                query = query.filter_by(action=request.args['action'])

            logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()
            return [log.to_dict() for log in logs]

    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(orgs_ns, path='/organizations')
    api.add_namespace(users_ns, path='/users')
    api.add_namespace(posts_ns, path='/posts')
    api.add_namespace(audit_ns, path='/audit-logs')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*80)
    print("MULTI-TENANT BLOG PLATFORM API - DEMO")
    print("="*80)
    print("\n✨ FEATURES:")
    print("  ✅ Multi-tenant architecture (organizations)")
    print("  ✅ Complete CRUD for organizations, users, and posts")
    print("  ✅ Database relationships (one-to-many)")
    print("  ✅ Audit logging for compliance")
    print("  ✅ Soft deletes with restore capability")
    print("  ✅ Query optimization (indexes + eager loading)")
    print("  ✅ Proper error handling")
    print("\n🚀 QUICK START:")
    print("  1. Create an organization: POST /organizations")
    print("  2. Create users in the org: POST /users")
    print("  3. Create posts: POST /posts")
    print("  4. View audit trail: GET /audit-logs")
    print("  5. Soft delete and restore: DELETE + POST /users/1/restore")
    print("\n📚 LEARNING HIGHLIGHTS:")
    print("  - Multi-tenancy: Data isolated by organization_id")
    print("  - Audit trail: All changes logged to audit_logs table")
    print("  - Soft deletes: deleted_at column instead of actual deletion")
    print("  - N+1 prevention: joinedload() for eager loading")
    print("  - Indexes: Composite indexes for common query patterns")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("🗄️  Supabase UI: View your data in Supabase dashboard")
    print("="*80 + "\n")

    app.run(debug=True, port=5000)
