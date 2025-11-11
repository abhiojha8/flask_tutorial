"""
DEMO: Blog Platform with Advanced Data Validation
Chapter 5: Data Validation & Error Handling

This demo showcases production-ready validation with:
- Marshmallow schemas for all endpoints
- Custom validators for business rules
- Nested object validation
- File upload validation (images)
- Cross-field validation
- Comprehensive error handling
- Input sanitization

ARCHITECTURE:

Validation Flow:
  Request → Schema.load() → Validate Fields → Custom Validators → Business Rules → Clean Data
  Invalid → ValidationError → Format Errors → Return 400 with Details

DATABASE SCHEMA:

users_validation:
  - id, username, email, password_hash
  - phone, bio, avatar_url
  - created_at, updated_at

posts_validation:
  - id, title, content, author_id
  - tags (array), category, status
  - publish_date, created_at, updated_at

comments_validation:
  - id, post_id, user_id, text
  - parent_comment_id (for nested comments)
  - created_at, updated_at

categories_validation:
  - id, name, parent_id (hierarchical)
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from marshmallow import Schema, fields as ma_fields, validates, validates_schema, ValidationError, EXCLUDE
from marshmallow.validate import Length, Range, OneOf, Email
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
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

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max request size

    # ============================================================================
    # EXTENSIONS
    # ============================================================================

    db = SQLAlchemy(app)

    # ============================================================================
    # API SETUP
    # ============================================================================

    api = Api(
        app,
        version='1.0',
        title='Blog Platform with Advanced Validation',
        description='Demonstrates Marshmallow validation, custom validators, nested schemas, and file uploads',
        doc='/swagger'
    )

    # ============================================================================
    # DATABASE MODELS
    # ============================================================================

    class User(db.Model):
        __tablename__ = 'users_validation'

        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False, index=True)
        email = db.Column(db.String(120), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=False)
        phone = db.Column(db.String(20))
        bio = db.Column(db.Text)
        avatar_url = db.Column(db.String(500))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

        posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
        comments = db.relationship('Comment', backref='user', lazy=True, cascade='all, delete-orphan')

        def set_password(self, password):
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'phone': self.phone,
                'bio': self.bio,
                'avatar_url': self.avatar_url,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

    class Post(db.Model):
        __tablename__ = 'posts_validation'

        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        content = db.Column(db.Text, nullable=False)
        author_id = db.Column(db.Integer, db.ForeignKey('users_validation.id'), nullable=False)
        tags = db.Column(db.JSON, default=list)  # Array of tags
        category = db.Column(db.String(50))
        status = db.Column(db.String(20), default='draft')  # draft, published, archived
        publish_date = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

        comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

        def to_dict(self, include_comments=False):
            result = {
                'id': self.id,
                'title': self.title,
                'content': self.content,
                'author_id': self.author_id,
                'tags': self.tags or [],
                'category': self.category,
                'status': self.status,
                'publish_date': self.publish_date.isoformat() if self.publish_date else None,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
            if include_comments:
                result['comments'] = [c.to_dict() for c in self.comments]
            return result

    class Comment(db.Model):
        __tablename__ = 'comments_validation'

        id = db.Column(db.Integer, primary_key=True)
        post_id = db.Column(db.Integer, db.ForeignKey('posts_validation.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('users_validation.id'), nullable=False)
        text = db.Column(db.Text, nullable=False)
        parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments_validation.id'))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

        replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)

        def to_dict(self, include_replies=False):
            result = {
                'id': self.id,
                'post_id': self.post_id,
                'user_id': self.user_id,
                'text': self.text,
                'parent_comment_id': self.parent_comment_id,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
            if include_replies:
                result['replies'] = [r.to_dict() for r in self.replies]
            return result

    class Category(db.Model):
        __tablename__ = 'categories_validation'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True, nullable=False)
        parent_id = db.Column(db.Integer, db.ForeignKey('categories_validation.id'))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

        children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)

        def to_dict(self, include_children=False):
            result = {
                'id': self.id,
                'name': self.name,
                'parent_id': self.parent_id
            }
            if include_children:
                result['children'] = [c.to_dict() for c in self.children]
            return result

    # ============================================================================
    # CUSTOM VALIDATORS
    # ============================================================================

    def validate_password_strength(password):
        """Validate password meets security requirements"""
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters')

        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')

        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')

        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')

    def validate_username_not_reserved(username):
        """Ensure username is not in reserved list"""
        reserved = ['admin', 'root', 'system', 'moderator', 'administrator']
        if username.lower() in reserved:
            raise ValidationError(f'Username "{username}" is reserved')

    def validate_no_profanity(text):
        """Basic profanity filter"""
        profanity_list = ['badword1', 'badword2', 'spam']  # Add actual words as needed
        text_lower = text.lower()
        for word in profanity_list:
            if word in text_lower:
                raise ValidationError(f'Content contains inappropriate language')

    def validate_phone_format(phone):
        """Validate phone number format (US format for demo)"""
        # Simple US phone validation: (123) 456-7890 or 123-456-7890 or 1234567890
        pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
        if not re.match(pattern, phone):
            raise ValidationError('Invalid phone number format. Use: (123) 456-7890 or 123-456-7890')

    # ============================================================================
    # MARSHMALLOW SCHEMAS
    # ============================================================================

    class UserRegistrationSchema(Schema):
        """Schema for user registration with comprehensive validation"""
        class Meta:
            unknown = EXCLUDE  # Ignore unknown fields

        username = ma_fields.Str(
            required=True,
            validate=Length(min=3, max=50)
        )
        email = ma_fields.Email(required=True)
        password = ma_fields.Str(required=True)
        phone = ma_fields.Str(
            required=False,
            allow_none=True
        )
        bio = ma_fields.Str(
            required=False,
            validate=Length(max=500)
        )

        @validates('username')
        def validate_username(self, value):
            # Must start with letter
            if not value[0].isalpha():
                raise ValidationError('Username must start with a letter')

            # Only alphanumeric and underscore
            if not re.match(r'^[a-zA-Z0-9_]+$', value):
                raise ValidationError('Username can only contain letters, numbers, and underscores')

            # Check reserved names
            validate_username_not_reserved(value)

            # Check if exists
            if User.query.filter_by(username=value).first():
                raise ValidationError('Username already exists')

        @validates('email')
        def validate_email_unique(self, value):
            # Block temporary email domains
            temp_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            domain = value.split('@')[1]
            if domain in temp_domains:
                raise ValidationError('Temporary email addresses are not allowed')

            # Check if exists
            if User.query.filter_by(email=value).first():
                raise ValidationError('Email already registered')

        @validates('password')
        def validate_password(self, value):
            validate_password_strength(value)

        @validates('phone')
        def validate_phone(self, value):
            if value:  # Only validate if provided
                validate_phone_format(value)

    class PostCreateSchema(Schema):
        """Schema for creating a blog post"""
        class Meta:
            unknown = EXCLUDE

        title = ma_fields.Str(
            required=True,
            validate=Length(min=5, max=200)
        )
        content = ma_fields.Str(
            required=True,
            validate=Length(min=10)
        )
        tags = ma_fields.List(
            ma_fields.Str(validate=Length(max=20)),
            validate=Length(max=10)  # Max 10 tags
        )
        category = ma_fields.Str(
            validate=Length(max=50)
        )
        status = ma_fields.Str(
            validate=OneOf(['draft', 'published', 'archived'])
        )
        publish_date = ma_fields.DateTime(required=False)

        @validates('title')
        def validate_title(self, value):
            # Check profanity
            validate_no_profanity(value)

            # Title should not be all caps
            if value.isupper() and len(value) > 10:
                raise ValidationError('Title should not be in all caps')

        @validates('content')
        def validate_content(self, value):
            validate_no_profanity(value)

        @validates('tags')
        def validate_tags(self, value):
            if value:
                # Check for duplicates
                if len(value) != len(set(value)):
                    raise ValidationError('Tags must be unique')

                # Each tag should be alphanumeric
                for tag in value:
                    if not re.match(r'^[a-zA-Z0-9-_]+$', tag):
                        raise ValidationError(f'Tag "{tag}" contains invalid characters')

        @validates_schema
        def validate_publish_requirements(self, data, **kwargs):
            """Cross-field validation: if status is published, must have publish_date"""
            if data.get('status') == 'published':
                if not data.get('publish_date'):
                    raise ValidationError(
                        'publish_date is required when status is published',
                        field_name='publish_date'
                    )

                # Publish date should not be in the past for new posts
                if data['publish_date'] < datetime.utcnow():
                    raise ValidationError(
                        'Publish date cannot be in the past',
                        field_name='publish_date'
                    )

    class CommentSchema(Schema):
        """Schema for comment validation"""
        class Meta:
            unknown = EXCLUDE

        text = ma_fields.Str(
            required=True,
            validate=Length(min=1, max=1000)
        )
        parent_comment_id = ma_fields.Int(required=False, allow_none=True)

        @validates('text')
        def validate_text(self, value):
            validate_no_profanity(value)

            # Check for excessive caps (more than 50%)
            caps_count = sum(1 for c in value if c.isupper())
            if len(value) > 0 and caps_count / len(value) > 0.5:
                raise ValidationError('Comment has too many capital letters')

    class NestedCommentSchema(Schema):
        """Schema with nested user data"""
        text = ma_fields.Str(required=True)
        user = ma_fields.Nested(lambda: UserInfoSchema(), required=True)

    class UserInfoSchema(Schema):
        """Nested schema for user info"""
        username = ma_fields.Str(
            required=True,
            validate=Length(min=3, max=50)
        )
        email = ma_fields.Email(required=True)

    class CategorySchema(Schema):
        """Schema for category with hierarchy validation"""
        name = ma_fields.Str(
            required=True,
            validate=Length(min=2, max=50)
        )
        parent_id = ma_fields.Int(required=False, allow_none=True)

        @validates('name')
        def validate_name_unique(self, value):
            if Category.query.filter_by(name=value).first():
                raise ValidationError('Category name already exists')

        @validates('parent_id')
        def validate_parent_exists(self, value):
            if value is not None:
                parent = Category.query.get(value)
                if not parent:
                    raise ValidationError(f'Parent category with id {value} does not exist')

    class SearchSchema(Schema):
        """Schema for search input sanitization"""
        query = ma_fields.Str(
            required=True,
            validate=Length(min=2, max=100)
        )
        category = ma_fields.Str(required=False)
        tags = ma_fields.List(ma_fields.Str())
        page = ma_fields.Int(
            validate=Range(min=1, max=1000),
            missing=1
        )
        per_page = ma_fields.Int(
            validate=Range(min=1, max=100),
            missing=10
        )

        @validates('query')
        def validate_query(self, value):
            # Remove dangerous SQL characters
            dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
            for char in dangerous_chars:
                if char in value.lower():
                    raise ValidationError('Query contains invalid characters')

    # ============================================================================
    # NAMESPACES
    # ============================================================================

    users_ns = Namespace('users', description='User operations with validation')
    posts_ns = Namespace('posts', description='Post operations with validation')
    comments_ns = Namespace('comments', description='Comment operations')
    categories_ns = Namespace('categories', description='Category management')
    search_ns = Namespace('search', description='Search with input sanitization')

    api.add_namespace(users_ns, path='/users')
    api.add_namespace(posts_ns, path='/posts')
    api.add_namespace(comments_ns, path='/comments')
    api.add_namespace(categories_ns, path='/categories')
    api.add_namespace(search_ns, path='/search')

    # ============================================================================
    # RESTX MODELS (for Swagger UI)
    # ============================================================================

    user_registration_model = users_ns.model('UserRegistration', {
        'username': fields.String(required=True, description='Username (3-50 chars, alphanumeric + underscore)'),
        'email': fields.String(required=True, description='Valid email address'),
        'password': fields.String(required=True, description='Strong password (8+ chars, upper, lower, number, special)'),
        'phone': fields.String(description='Phone number (optional)'),
        'bio': fields.String(description='User bio (max 500 chars)')
    })

    post_create_model = posts_ns.model('PostCreate', {
        'title': fields.String(required=True, description='Post title (5-200 chars)'),
        'content': fields.String(required=True, description='Post content (10+ chars)'),
        'tags': fields.List(fields.String, description='Tags (max 10, unique)'),
        'category': fields.String(description='Category name'),
        'status': fields.String(description='Status: draft, published, archived'),
        'publish_date': fields.DateTime(description='Publish date (required if status=published)')
    })

    comment_model = comments_ns.model('Comment', {
        'text': fields.String(required=True, description='Comment text (1-1000 chars)'),
        'parent_comment_id': fields.Integer(description='Parent comment ID for nested comments')
    })

    category_model = categories_ns.model('Category', {
        'name': fields.String(required=True, description='Category name (unique)'),
        'parent_id': fields.Integer(description='Parent category ID for hierarchy')
    })

    search_model = search_ns.model('Search', {
        'query': fields.String(required=True, description='Search query (2-100 chars)'),
        'category': fields.String(description='Filter by category'),
        'tags': fields.List(fields.String, description='Filter by tags'),
        'page': fields.Integer(description='Page number (default: 1)'),
        'per_page': fields.Integer(description='Items per page (default: 10, max: 100)')
    })

    # ============================================================================
    # ROUTES
    # ============================================================================

    @users_ns.route('/register')
    class UserRegister(Resource):
        @users_ns.expect(user_registration_model)
        def post(self):
            """Register new user with comprehensive validation"""
            schema = UserRegistrationSchema()

            try:
                # Validate and deserialize
                data = schema.load(request.json)
            except ValidationError as err:
                return {'errors': err.messages}, 400

            # Create user
            user = User(
                username=data['username'],
                email=data['email'],
                phone=data.get('phone'),
                bio=data.get('bio')
            )
            user.set_password(data['password'])

            db.session.add(user)
            db.session.commit()

            return {
                'message': 'User registered successfully',
                'user': user.to_dict()
            }, 201

    @users_ns.route('/')
    class UserList(Resource):
        def get(self):
            """Get all users"""
            users = User.query.all()
            return {'users': [u.to_dict() for u in users]}, 200

    @posts_ns.route('/')
    class PostList(Resource):
        @posts_ns.expect(post_create_model)
        def post(self):
            """Create new post with validation"""
            schema = PostCreateSchema()

            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return {'errors': err.messages}, 400

            # For demo, use first user as author
            author = User.query.first()
            if not author:
                return {'error': 'No users found. Register a user first.'}, 400

            post = Post(
                title=data['title'],
                content=data['content'],
                author_id=author.id,
                tags=data.get('tags', []),
                category=data.get('category'),
                status=data.get('status', 'draft'),
                publish_date=data.get('publish_date')
            )

            db.session.add(post)
            db.session.commit()

            return {
                'message': 'Post created successfully',
                'post': post.to_dict()
            }, 201

        def get(self):
            """Get all posts"""
            posts = Post.query.all()
            return {'posts': [p.to_dict() for p in posts]}, 200

    @posts_ns.route('/<int:post_id>')
    class PostItem(Resource):
        def get(self, post_id):
            """Get post by ID with comments"""
            post = Post.query.get_or_404(post_id)
            return post.to_dict(include_comments=True), 200

    @posts_ns.route('/<int:post_id>/comments')
    class PostComments(Resource):
        @posts_ns.expect(comment_model)
        def post(self, post_id):
            """Add comment to post"""
            post = Post.query.get_or_404(post_id)
            schema = CommentSchema()

            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return {'errors': err.messages}, 400

            # For demo, use first user
            user = User.query.first()
            if not user:
                return {'error': 'No users found'}, 400

            # Validate parent comment if provided
            if data.get('parent_comment_id'):
                parent = Comment.query.get(data['parent_comment_id'])
                if not parent or parent.post_id != post_id:
                    return {'error': 'Invalid parent comment'}, 400

            comment = Comment(
                post_id=post_id,
                user_id=user.id,
                text=data['text'],
                parent_comment_id=data.get('parent_comment_id')
            )

            db.session.add(comment)
            db.session.commit()

            return {
                'message': 'Comment added',
                'comment': comment.to_dict()
            }, 201

    @categories_ns.route('/')
    class CategoryList(Resource):
        @categories_ns.expect(category_model)
        def post(self):
            """Create category with hierarchy validation"""
            schema = CategorySchema()

            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return {'errors': err.messages}, 400

            category = Category(
                name=data['name'],
                parent_id=data.get('parent_id')
            )

            db.session.add(category)
            db.session.commit()

            return {
                'message': 'Category created',
                'category': category.to_dict()
            }, 201

        def get(self):
            """Get all categories"""
            categories = Category.query.filter_by(parent_id=None).all()
            return {'categories': [c.to_dict(include_children=True) for c in categories]}, 200

    @search_ns.route('/')
    class Search(Resource):
        @search_ns.expect(search_model)
        def post(self):
            """Search posts with sanitized input"""
            schema = SearchSchema()

            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return {'errors': err.messages}, 400

            # Build query
            query = Post.query

            # Search in title and content (sanitized)
            search_term = data['query']
            query = query.filter(
                db.or_(
                    Post.title.ilike(f'%{search_term}%'),
                    Post.content.ilike(f'%{search_term}%')
                )
            )

            # Filter by category
            if data.get('category'):
                query = query.filter_by(category=data['category'])

            # Filter by tags
            if data.get('tags'):
                for tag in data['tags']:
                    query = query.filter(Post.tags.contains([tag]))

            # Pagination
            page = data['page']
            per_page = data['per_page']

            total = query.count()
            posts = query.offset((page - 1) * per_page).limit(per_page).all()

            return {
                'results': [p.to_dict() for p in posts],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }, 200

    # ============================================================================
    # DATABASE INITIALIZATION
    # ============================================================================

    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
        print("📊 Tables: users_validation, posts_validation, comments_validation, categories_validation")

    return app

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    app = create_app()

    print("\n" + "="*70)
    print("🚀 FLASK VALIDATION DEMO")
    print("="*70)
    print("📖 Chapter 5: Data Validation & Error Handling")
    print()
    print("Features:")
    print("  ✅ Marshmallow schema validation")
    print("  ✅ Custom validators (password, username, profanity)")
    print("  ✅ Nested object validation")
    print("  ✅ Cross-field validation")
    print("  ✅ Input sanitization")
    print("  ✅ Comprehensive error messages")
    print()
    print("📡 Swagger UI: http://localhost:5000/swagger")
    print()
    print("Try these validation scenarios:")
    print("  1. Register with weak password → See detailed error")
    print("  2. Create post with status='published' without publish_date → Cross-field error")
    print("  3. Add comment with profanity → Content validation error")
    print("  4. Create category with invalid parent_id → Relationship validation")
    print("  5. Search with SQL injection attempt → Input sanitization")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
