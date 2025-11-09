"""
Exercise 2: One-to-Many Relationships - Blog Posts API

OBJECTIVE:
Build on Exercise 1 by adding a Posts table with a one-to-many relationship.
One user can have many posts, but each post belongs to only one user.

WHAT YOU'LL BUILD:
- Post model with foreign key to User
- One-to-many relationship (User → Posts)
- CRUD API for posts
- Nested resource: GET /users/<id>/posts
- Cascade deletes (when user deleted, their posts are deleted)
- Eager vs lazy loading

LEARNING GOALS:
- Define foreign keys in SQLAlchemy
- Set up relationships with backref
- Understand cascade behavior
- Prevent N+1 query problems
- Work with nested resources

DATABASE SCHEMA:

users table (from Exercise 1):
- id: Integer, Primary Key
- username: String(80), Unique, Not Null
- email: String(120), Unique, Not Null
- full_name: String(100), Nullable
- is_active: Boolean, Default True
- created_at: DateTime, Default UTC now
- updated_at: DateTime, Default UTC now, Auto-update

posts table (NEW):
- id: Integer, Primary Key, Auto-increment
- user_id: Integer, Foreign Key → users.id, Not Null
- title: String(200), Not Null
- content: Text, Nullable
- status: String(20), Default 'draft' (draft/published/archived)
- view_count: Integer, Default 0
- created_at: DateTime, Default UTC now
- updated_at: DateTime, Default UTC now, Auto-update

Relationship: User ─< Post (one-to-many)

API ENDPOINTS:
- POST /posts - Create new post
- GET /posts - List all posts (with author info)
- GET /posts/<id> - Get single post (with author info)
- PUT /posts/<id> - Update post
- DELETE /posts/<id> - Delete post
- GET /users/<id>/posts - Get all posts by a specific user (nested resource)

TODO CHECKLIST:
[ ] Define Post model with user_id foreign key
[ ] Add 'posts' relationship to User model
[ ] Implement POST /posts (validate user_id exists)
[ ] Implement GET /posts (include author information)
[ ] Implement GET /posts/<id>
[ ] Implement PUT /posts/<id>
[ ] Implement DELETE /posts/<id>
[ ] Implement GET /users/<id>/posts (nested resource)
[ ] Configure cascade delete (user deletion → posts deletion)
[ ] Use eager loading to avoid N+1 queries
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy.orm import joinedload

# Load environment variables
load_dotenv()

def create_app():
    """
    Create and configure the Blog Posts API.

    This builds on Exercise 1 by adding relationships!
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

    # Initialize Flask-RESTX
    api = Api(
        app,
        version='1.0',
        title='Blog Posts API',
        description='Exercise 2: One-to-Many Relationships (User → Posts)',
        doc='/swagger'
    )

    # ============================================================================
    # DATABASE INITIALIZATION
    # ============================================================================

    db = SQLAlchemy(app)

    # ============================================================================
    # DATABASE MODELS
    # ============================================================================

    class User(db.Model):
        """
        User model from Exercise 1.

        NEW: Added 'posts' relationship to access user's posts.
        """
        __tablename__ = 'users'

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        full_name = db.Column(db.String(100), nullable=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # TODO: Add relationship to posts
        # HINT: posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
        #
        # WHAT THIS MEANS:
        # - 'Post': The related model
        # - backref='author': Creates Post.author to access the user
        # - lazy=True: Load posts only when accessed (lazy loading)
        # - cascade='all, delete-orphan': When user is deleted, delete their posts too
        #
        # AFTER THIS, YOU CAN DO:
        # user.posts → Get all posts by this user
        # post.author → Get the user who wrote this post

        def to_dict(self):
            """Convert User to dictionary."""
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }

    # TODO: Define Post model
    # HINT: class Post(db.Model):

    class Post(db.Model):
        """
        Post model representing a blog post.

        NEW CONCEPT: This model has a FOREIGN KEY to the User model.
        Each post belongs to exactly one user (the author).
        """
        __tablename__ = 'posts'

        # TODO: Define all columns
        # HINT: user_id should be db.ForeignKey('users.id'), nullable=False
        # HINT: status should have a default value of 'draft'
        # HINT: view_count should have a default value of 0

        id = None  # TODO: db.Column(db.Integer, primary_key=True)
        user_id = None  # TODO: db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        title = None  # TODO: db.Column(db.String(200), nullable=False)
        content = None  # TODO: db.Column(db.Text, nullable=True)
        status = None  # TODO: db.Column(db.String(20), default='draft')
        view_count = None  # TODO: db.Column(db.Integer, default=0)
        created_at = None  # TODO: db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = None  # TODO: db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def to_dict(self, include_author=False):
            """
            Convert Post to dictionary.

            NEW: include_author parameter allows including author information.
            This is useful when you want to show who wrote the post.

            Args:
                include_author: If True, includes author details in the response
            """
            # TODO: Return dictionary with all post fields
            # HINT: If include_author is True, add 'author': self.author.to_dict()
            # HINT: This uses the 'author' backref created by the relationship
            # HINT: Format datetime fields as ISO strings
            pass

    # ============================================================================
    # CREATE TABLES
    # ============================================================================

    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
        print("   - users table (from Exercise 1)")
        print("   - posts table (NEW with foreign key to users)")

    # ============================================================================
    # API MODELS (for Swagger)
    # ============================================================================

    users_ns = Namespace('users', description='User operations')
    posts_ns = Namespace('posts', description='Post operations')

    # User models (from Exercise 1)
    user_output_model = users_ns.model('User', {
        'id': fields.Integer(description='User ID'),
        'username': fields.String(description='Username'),
        'email': fields.String(description='Email'),
        'full_name': fields.String(description='Full name'),
        'is_active': fields.Boolean(description='Active status'),
        'created_at': fields.String(description='Creation timestamp'),
        'updated_at': fields.String(description='Update timestamp')
    })

    # Post input model
    post_input_model = posts_ns.model('PostInput', {
        'user_id': fields.Integer(required=True, description='Author user ID', example=1),
        'title': fields.String(required=True, description='Post title', example='My First Blog Post'),
        'content': fields.String(required=False, description='Post content', example='This is the content...'),
        'status': fields.String(required=False, description='Status', enum=['draft', 'published', 'archived'], example='draft'),
        'view_count': fields.Integer(required=False, description='View count', example=0)
    })

    # Post output model (with optional author)
    post_output_model = posts_ns.model('Post', {
        'id': fields.Integer(description='Post ID'),
        'user_id': fields.Integer(description='Author user ID'),
        'title': fields.String(description='Title'),
        'content': fields.String(description='Content'),
        'status': fields.String(description='Status'),
        'view_count': fields.Integer(description='View count'),
        'created_at': fields.String(description='Creation timestamp'),
        'updated_at': fields.String(description='Update timestamp'),
        'author': fields.Nested(user_output_model, description='Author information', skip_none=True)
    })

    # ============================================================================
    # POST ENDPOINTS
    # ============================================================================

    @posts_ns.route('/')
    class PostList(Resource):
        """Post collection endpoints"""

        @posts_ns.doc('list_posts')
        @posts_ns.marshal_list_with(post_output_model)
        def get(self):
            """
            List all posts with author information.

            TODO: Query all posts and include author info.

            IMPORTANT: Use eager loading to avoid N+1 queries!

            N+1 PROBLEM:
            ❌ Bad:
                posts = Post.query.all()  # 1 query
                for post in posts:
                    print(post.author.username)  # N queries (one per post!)

            ✅ Good:
                posts = Post.query.options(joinedload(Post.author)).all()  # 1 query with JOIN
            """
            # TODO: Implement GET /posts
            # HINT: Use Post.query.options(joinedload(Post.author)).all()
            # HINT: Convert each post with to_dict(include_author=True)
            pass

        @posts_ns.doc('create_post')
        @posts_ns.expect(post_input_model)
        @posts_ns.marshal_with(post_output_model, code=201)
        @posts_ns.response(400, 'Validation Error')
        @posts_ns.response(404, 'User not found')
        def post(self):
            """
            Create a new post.

            TODO: Create post linked to a user.

            VALIDATION:
            - user_id must exist in users table
            - title is required

            STEPS:
            1. Get JSON data
            2. Validate user_id exists (User.query.get(user_id))
            3. If user doesn't exist, return 404
            4. Create Post object
            5. Add and commit
            6. Return with author info
            """
            # TODO: Implement POST /posts
            # HINT: Check if user exists first: user = User.query.get(data['user_id'])
            # HINT: If not user, return {'message': 'User not found'}, 404
            # HINT: Create post: post = Post(title=..., user_id=..., ...)
            pass

    @posts_ns.route('/<int:id>')
    @posts_ns.param('id', 'Post identifier')
    class PostItem(Resource):
        """Single post endpoints"""

        @posts_ns.doc('get_post')
        @posts_ns.marshal_with(post_output_model)
        @posts_ns.response(404, 'Post not found')
        def get(self, id):
            """
            Get post by ID with author information.

            TODO: Get single post with eager loaded author.
            """
            # TODO: Implement GET /posts/<id>
            # HINT: Post.query.options(joinedload(Post.author)).get_or_404(id)
            # HINT: Return post.to_dict(include_author=True)
            pass

        @posts_ns.doc('update_post')
        @posts_ns.expect(post_input_model)
        @posts_ns.marshal_with(post_output_model)
        @posts_ns.response(404, 'Post not found')
        def put(self, id):
            """
            Update post.

            TODO: Update post fields.

            NOTE: You can allow changing the user_id, but validate it exists!
            """
            # TODO: Implement PUT /posts/<id>
            # HINT: Get post by ID
            # HINT: If changing user_id, validate new user exists
            # HINT: Update fields from request.json
            # HINT: db.session.commit()
            pass

        @posts_ns.doc('delete_post')
        @posts_ns.response(204, 'Post deleted')
        @posts_ns.response(404, 'Post not found')
        def delete(self, id):
            """
            Delete post.

            TODO: Remove post from database.
            """
            # TODO: Implement DELETE /posts/<id>
            # HINT: Similar to Exercise 1
            pass

    # ============================================================================
    # NESTED RESOURCE: USER'S POSTS
    # ============================================================================

    @users_ns.route('/<int:id>/posts')
    @users_ns.param('id', 'User identifier')
    class UserPosts(Resource):
        """Nested resource: Get all posts by a specific user"""

        @users_ns.doc('get_user_posts')
        @users_ns.marshal_list_with(post_output_model)
        @users_ns.response(404, 'User not found')
        def get(self, id):
            """
            Get all posts by a specific user.

            TODO: This is a NESTED RESOURCE endpoint.

            TWO APPROACHES:

            Approach 1 - Use the relationship:
                user = User.query.get_or_404(id)
                posts = user.posts  # Uses the relationship we defined!

            Approach 2 - Query posts with filter:
                Post.query.filter_by(user_id=id).all()

            Both are valid. Approach 1 is more Pythonic.
            """
            # TODO: Implement GET /users/<id>/posts
            # HINT: First verify user exists
            # HINT: Return user.posts (uses the relationship!)
            # HINT: Convert each post to dict
            pass

    # ============================================================================
    # USER ENDPOINTS (from Exercise 1, kept for reference)
    # ============================================================================

    @users_ns.route('/')
    class UserList(Resource):
        """User collection endpoints (from Exercise 1)"""

        @users_ns.doc('list_users')
        @users_ns.marshal_list_with(user_output_model)
        def get(self):
            """List all users."""
            users = User.query.all()
            return [user.to_dict() for user in users]

    @users_ns.route('/<int:id>')
    @users_ns.param('id', 'User identifier')
    class UserItem(Resource):
        """Single user endpoints"""

        @users_ns.doc('get_user')
        @users_ns.marshal_with(user_output_model)
        @users_ns.response(404, 'User not found')
        def get(self, id):
            """Get user by ID."""
            user = User.query.get_or_404(id)
            return user.to_dict()

    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(users_ns, path='/users')
    api.add_namespace(posts_ns, path='/posts')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("BLOG POSTS API - Exercise 2: One-to-Many Relationships")
    print("="*70)
    print("📚 Learning Objectives:")
    print("  - Define foreign keys in SQLAlchemy")
    print("  - Create one-to-many relationships")
    print("  - Use eager loading to prevent N+1 queries")
    print("  - Work with nested resources")
    print("  - Understand cascade deletes")
    print("\n🎯 Test Your Implementation:")
    print("  1. Create a user first (you need one for user_id)")
    print("  2. Create a post: POST /posts with user_id")
    print("  3. List all posts: GET /posts (should include author info)")
    print("  4. Get user's posts: GET /users/1/posts")
    print("  5. Delete a user and check if their posts are deleted too")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("🗄️  Check Supabase UI to see the relationship!")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
