"""
Exercise 3: Multi-tenant Design - Organizations

OBJECTIVE:
Implement multi-tenant architecture where data is isolated by organization.
This is how SaaS applications work - each company has its own data space.

WHAT YOU'LL BUILD:
- Organization model (tenants)
- Modified User and Post models with organization_id
- Tenant isolation - users can only see their organization's data
- Organization-scoped endpoints
- Proper data filtering by tenant

LEARNING GOALS:
- Understand multi-tenant architecture patterns
- Implement tenant isolation in database design
- Filter queries by organization context
- Prevent cross-tenant data leakage
- Design SaaS-ready database schemas

MULTI-TENANT EXPLAINED:

Think of a project management tool like Asana or Trello:
- Company A (Acme Corp) has users Alice and Bob
- Company B (Tech Inc) has users Charlie and Diana
- Alice should NEVER see Charlie's data, even though they're in the same database!

This is multi-tenancy: multiple organizations (tenants) sharing the same application
but with completely isolated data.

DATABASE SCHEMA:

organizations table (NEW):
- id: Integer, Primary Key
- name: String(100), Unique, Not Null
- slug: String(50), Unique, Not Null  # URL-friendly identifier
- plan: String(20), Default 'free'  # free/pro/enterprise
- is_active: Boolean, Default True
- created_at: DateTime, Default UTC now
- updated_at: DateTime, Default UTC now, Auto-update

users table (MODIFIED from Exercise 2):
- ... (all previous fields)
- organization_id: Integer, Foreign Key → organizations.id, Not Null

posts table (MODIFIED from Exercise 2):
- ... (all previous fields)
- organization_id: Integer, Foreign Key → organizations.id, Not Null

Relationships:
- Organization ─< User (one-to-many)
- Organization ─< Post (one-to-many)
- User ─< Post (one-to-many, from Exercise 2)

API ENDPOINTS:
- POST /organizations - Create organization
- GET /organizations - List all organizations
- GET /organizations/<id> - Get organization
- GET /organizations/<id>/users - Get organization's users
- GET /organizations/<id>/posts - Get organization's posts
- All previous user/post endpoints now filtered by organization

TODO CHECKLIST:
[ ] Create Organization model
[ ] Add organization_id to User model
[ ] Add organization_id to Post model
[ ] Implement Organization CRUD endpoints
[ ] Implement GET /organizations/<id>/users
[ ] Implement GET /organizations/<id>/posts
[ ] Add organization filtering to user/post queries
[ ] Validate organization_id when creating users/posts
[ ] Prevent cross-organization data access
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload

load_dotenv()

def create_app():
    """
    Create and configure the Multi-tenant Blog API.

    This demonstrates how SaaS applications isolate customer data!
    """
    app = Flask(__name__)
    CORS(app)

    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables!")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    api = Api(
        app,
        version='1.0',
        title='Multi-tenant Blog API',
        description='Exercise 3: Organizations and Tenant Isolation',
        doc='/swagger'
    )

    # ============================================================================
    # DATABASE INITIALIZATION
    # ============================================================================

    db = SQLAlchemy(app)

    # ============================================================================
    # DATABASE MODELS
    # ============================================================================

    # TODO: Define Organization model
    # HINT: class Organization(db.Model):

    class Organization(db.Model):
        """
        Organization model representing a tenant.

        Each organization is a separate company/team using your application.
        Their data is completely isolated from other organizations.
        """
        __tablename__ = 'organizations'

        # TODO: Define all columns
        # HINT: slug should be unique and URL-friendly (e.g., 'acme-corp')
        # HINT: plan should default to 'free'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False, index=True)
        slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
        plan = db.Column(db.String(20), default='free')
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Relationships
        # This allows:
        # - org.users → Get all users in this organization
        # - org.posts → Get all posts in this organization
        # - user.organization → Get the user's organization
        # - post.organization → Get the post's organization
        users = db.relationship('User', backref='organization', lazy=True)
        posts = db.relationship('Post', backref='organization', lazy=True)

        def to_dict(self):
            """Convert Organization to dictionary."""
            return {
                'id': self.id,
                'name': self.name,
                'slug': self.slug,
                'plan': self.plan,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    class User(db.Model):
        """
        User model (MODIFIED from Exercise 2).

        NEW: Added organization_id foreign key.
        Users now belong to an organization.
        """
        __tablename__ = 'users'

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        full_name = db.Column(db.String(100), nullable=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Foreign key to organization
        organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)

        # Relationship to posts (from Exercise 2)
        posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

        def to_dict(self, include_organization=False):
            """Convert User to dictionary."""
            result = {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'is_active': self.is_active,
                'organization_id': self.organization_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

            # If include_organization, add organization details
            if include_organization and self.organization:
                result['organization'] = self.organization.to_dict()

            return result

    class Post(db.Model):
        """
        Post model (MODIFIED from Exercise 2).

        NEW: Added organization_id foreign key.
        Posts now belong to an organization.

        MULTI-TENANT RULE: A post's organization_id MUST match its author's organization_id!
        """
        __tablename__ = 'posts'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        title = db.Column(db.String(200), nullable=False)
        content = db.Column(db.Text, nullable=True)
        status = db.Column(db.String(20), default='draft')
        view_count = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Foreign key to organization
        organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False, index=True)

        def to_dict(self, include_author=False, include_organization=False):
            """Convert Post to dictionary."""
            result = {
                'id': self.id,
                'user_id': self.user_id,
                'organization_id': self.organization_id,
                'title': self.title,
                'content': self.content,
                'status': self.status,
                'view_count': self.view_count,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

            # If include_author, add author details
            if include_author and self.author:
                result['author'] = self.author.to_dict()

            # If include_organization, add organization details
            if include_organization and self.organization:
                result['organization'] = self.organization.to_dict()

            return result

    # ============================================================================
    # CREATE TABLES
    # ============================================================================

    with app.app_context():
        db.create_all()
        print("[OK] Database tables created successfully!")
        print("   - organizations table (NEW)")
        print("   - users table (with organization_id)")
        print("   - posts table (with organization_id)")

    # ============================================================================
    # API MODELS
    # ============================================================================

    orgs_ns = Namespace('organizations', description='Organization management')
    users_ns = Namespace('users', description='User operations')
    posts_ns = Namespace('posts', description='Post operations')

    # Organization models
    org_input_model = orgs_ns.model('OrganizationInput', {
        'name': fields.String(required=True, description='Organization name', example='Acme Corporation'),
        'slug': fields.String(required=True, description='URL-friendly identifier', example='acme-corp'),
        'plan': fields.String(required=False, description='Plan type', enum=['free', 'pro', 'enterprise'], example='pro'),
        'is_active': fields.Boolean(required=False, description='Active status', example=True)
    })

    org_output_model = orgs_ns.model('Organization', {
        'id': fields.Integer(description='Organization ID'),
        'name': fields.String(description='Name'),
        'slug': fields.String(description='Slug'),
        'plan': fields.String(description='Plan'),
        'is_active': fields.Boolean(description='Active status'),
        'created_at': fields.String(description='Created timestamp'),
        'updated_at': fields.String(description='Updated timestamp')
    })

    # User models (with organization_id)
    user_output_model = users_ns.model('User', {
        'id': fields.Integer(description='User ID'),
        'username': fields.String(description='Username'),
        'email': fields.String(description='Email'),
        'full_name': fields.String(description='Full name'),
        'is_active': fields.Boolean(description='Active status'),
        'organization_id': fields.Integer(description='Organization ID'),
        'created_at': fields.String(description='Created timestamp'),
        'updated_at': fields.String(description='Updated timestamp')
    })

    # Post models (with organization_id)
    post_output_model = posts_ns.model('Post', {
        'id': fields.Integer(description='Post ID'),
        'user_id': fields.Integer(description='Author user ID'),
        'organization_id': fields.Integer(description='Organization ID'),
        'title': fields.String(description='Title'),
        'content': fields.String(description='Content'),
        'status': fields.String(description='Status'),
        'view_count': fields.Integer(description='View count'),
        'created_at': fields.String(description='Created timestamp'),
        'updated_at': fields.String(description='Updated timestamp')
    })

    # ============================================================================
    # ORGANIZATION ENDPOINTS
    # ============================================================================

    @orgs_ns.route('/')
    class OrganizationList(Resource):
        """Organization collection endpoints"""

        @orgs_ns.doc('list_organizations')
        @orgs_ns.marshal_list_with(org_output_model)
        def get(self):
            """
            List all organizations.

            Query all organizations.
            """
            organizations = Organization.query.all()
            return [org.to_dict() for org in organizations]

        @orgs_ns.doc('create_organization')
        @orgs_ns.expect(org_input_model)
        @orgs_ns.marshal_with(org_output_model, code=201)
        @orgs_ns.response(400, 'Validation Error')
        @orgs_ns.response(409, 'Organization already exists')
        def post(self):
            """
            Create a new organization.

            Create organization with validation.

            VALIDATION:
            - name must be unique
            - slug must be unique
            - slug should be URL-friendly (lowercase, hyphens, no spaces)
            """
            data = request.json

            # Check for duplicate name
            if Organization.query.filter_by(name=data['name']).first():
                return {'message': 'Organization name already exists'}, 409

            # Check for duplicate slug
            if Organization.query.filter_by(slug=data['slug']).first():
                return {'message': 'Organization slug already exists'}, 409

            # Create new organization
            org = Organization(
                name=data['name'],
                slug=data['slug'],
                plan=data.get('plan', 'free'),
                is_active=data.get('is_active', True)
            )

            db.session.add(org)
            db.session.commit()

            return org.to_dict(), 201

    @orgs_ns.route('/<int:id>')
    @orgs_ns.param('id', 'Organization identifier')
    class OrganizationItem(Resource):
        """Single organization endpoints"""

        @orgs_ns.doc('get_organization')
        @orgs_ns.marshal_with(org_output_model)
        @orgs_ns.response(404, 'Organization not found')
        def get(self, id):
            """
            Get organization by ID.

            Get single organization.
            """
            org = Organization.query.get_or_404(id)
            return org.to_dict()

    @orgs_ns.route('/<int:id>/users')
    @orgs_ns.param('id', 'Organization identifier')
    class OrganizationUsers(Resource):
        """Get all users in an organization"""

        @orgs_ns.doc('get_organization_users')
        @orgs_ns.marshal_list_with(user_output_model)
        @orgs_ns.response(404, 'Organization not found')
        def get(self, id):
            """
            Get all users in this organization.

            This is TENANT-SCOPED querying!

            APPROACH 1 - Use relationship:
                org = Organization.query.get_or_404(id)
                return org.users

            APPROACH 2 - Query with filter:
                User.query.filter_by(organization_id=id).all()

            Both work, but Approach 1 is cleaner.
            """
            # Verify organization exists first
            org = Organization.query.get_or_404(id)

            # Return all users in this organization
            return [user.to_dict() for user in org.users]

    @orgs_ns.route('/<int:id>/posts')
    @orgs_ns.param('id', 'Organization identifier')
    class OrganizationPosts(Resource):
        """Get all posts in an organization"""

        @orgs_ns.doc('get_organization_posts')
        @orgs_ns.marshal_list_with(post_output_model)
        @orgs_ns.response(404, 'Organization not found')
        def get(self, id):
            """
            Get all posts in this organization.

            Similar to OrganizationUsers, but for posts.

            BONUS: Use eager loading to include author info!
            Post.query.filter_by(organization_id=id).options(joinedload(Post.author)).all()
            """
            # Verify organization exists first
            org = Organization.query.get_or_404(id)

            # Use eager loading to prevent N+1 queries
            posts = Post.query.filter_by(organization_id=id).options(joinedload(Post.author)).all()

            # Return all posts in this organization with author info
            return [post.to_dict(include_author=True) for post in posts]

    # ============================================================================
    # MODIFIED ENDPOINTS (now with organization awareness)
    # ============================================================================

    # NOTE: In a real SaaS app, you would:
    # 1. Get the current user's organization from authentication
    # 2. Automatically filter all queries by that organization
    # 3. Users would NEVER see data from other organizations
    #
    # For this exercise, we're exposing organization_id in the API
    # so you can manually specify which organization you're working with.

    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(orgs_ns, path='/organizations')
    api.add_namespace(users_ns, path='/users')
    api.add_namespace(posts_ns, path='/posts')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("MULTI-TENANT BLOG API - Exercise 3: Organizations")
    print("="*70)
    print("📚 Learning Objectives:")
    print("  - Understand multi-tenant architecture")
    print("  - Implement tenant isolation with foreign keys")
    print("  - Filter queries by organization")
    print("  - Prevent cross-tenant data access")
    print("  - Design SaaS-ready schemas")
    print("\n🎯 Test Your Implementation:")
    print("  1. Create Organization A: POST /organizations")
    print("  2. Create Organization B: POST /organizations")
    print("  3. Create users in each organization")
    print("  4. Create posts in each organization")
    print("  5. GET /organizations/1/users (should only show Org A users)")
    print("  6. GET /organizations/2/posts (should only show Org B posts)")
    print("  7. Verify data isolation is working!")
    print("\n💡 Key Concept:")
    print("  This is how Slack, Asana, Trello, etc. work!")
    print("  Each company has completely isolated data.")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("🗄️  Check Supabase to see organization foreign keys!")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
