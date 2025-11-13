"""
Unified Backend API for Chapter 6: Frontend with Streamlit
Combines concepts from Chapters 1-5:
- RESTful API design (Chapter 2)
- Database integration (Chapter 3)
- JWT authentication (Chapter 4)
- Data validation (Chapter 5)

This backend serves as the API for the Streamlit frontend demo.
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from flask_cors import CORS
from marshmallow import Schema, fields as ma_fields, validates, validates_schema, ValidationError, EXCLUDE
from marshmallow.validate import Length, Range, OneOf
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from PIL import Image
import os
import re
import uuid
import bcrypt
from dotenv import load_dotenv

load_dotenv()

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
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================================
# EXTENSIONS
# ============================================================================

db = SQLAlchemy(app)
jwt = JWTManager(app)

api = Api(
    app,
    version='1.0',
    title='Unified Blog API',
    description='Complete blog API with authentication, validation, and CRUD operations for Streamlit frontend',
    doc='/swagger',
    prefix='/api',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type: **'Bearer &lt;JWT&gt;'**"
        }
    },
    security='Bearer'
)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    __tablename__ = 'users_frontend'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    articles = db.relationship('Article', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.username,  # Alias for frontend compatibility
            'email': self.email,
            'bio': self.bio,
            'article_count': len(self.articles),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Article(db.Model):
    __tablename__ = 'articles_frontend'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(250), unique=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users_frontend.id'), nullable=False)
    category = db.Column(db.String(50), index=True)
    tags = db.Column(db.JSON, default=list)
    published = db.Column(db.Boolean, default=False, index=True)
    views = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    comments = db.relationship('Comment', backref='article', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_author=True, include_comments=False):
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'slug': self.slug,
            'author_id': self.author_id,
            'category': self.category,
            'tags': self.tags or [],
            'published': self.published,
            'views': self.views,
            'image_url': self.image_url,
            'comment_count': len(self.comments),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_author and self.author:
            result['author'] = {
                'id': self.author.id,
                'name': self.author.username,
                'email': self.author.email
            }

        if include_comments:
            result['comments'] = [c.to_dict() for c in self.comments]

        return result

class Comment(db.Model):
    __tablename__ = 'comments_frontend'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles_frontend.id'), nullable=False)
    author_name = db.Column(db.String(50), nullable=False)
    author_email = db.Column(db.String(120), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'text': self.text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist_frontend'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def is_blacklisted(jti):
        return TokenBlacklist.query.filter_by(jti=jti).first() is not None

# ============================================================================
# JWT CALLBACKS
# ============================================================================

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return TokenBlacklist.is_blacklisted(jti)

# ============================================================================
# VALIDATION SCHEMAS (Marshmallow)
# ============================================================================

# Password strength validator
def validate_password_strength(password):
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

class UserRegistrationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = ma_fields.Str(required=True, validate=Length(min=3, max=50))
    email = ma_fields.Email(required=True)
    password = ma_fields.Str(required=True)
    bio = ma_fields.Str(required=False, validate=Length(max=500))

    @validates('username')
    def validate_username(self, value):
        if not value[0].isalpha():
            raise ValidationError('Username must start with a letter')

        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('Username can only contain letters, numbers, and underscores')

        reserved = ['admin', 'root', 'system', 'moderator']
        if value.lower() in reserved:
            raise ValidationError(f'Username "{value}" is reserved')

        if User.query.filter_by(username=value).first():
            raise ValidationError('Username already exists')

    @validates('email')
    def validate_email_unique(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already registered')

    @validates('password')
    def validate_password(self, value):
        validate_password_strength(value)

class UserLoginSchema(Schema):
    email = ma_fields.Email(required=True)
    password = ma_fields.Str(required=True)

class ArticleSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = ma_fields.Str(required=True, validate=Length(min=5, max=200))
    content = ma_fields.Str(required=True, validate=Length(min=50))
    category = ma_fields.Str(validate=OneOf(['Technology', 'Science', 'Business', 'Health', 'Sports']))
    tags = ma_fields.List(ma_fields.Str(validate=Length(max=20)), validate=Length(max=10))
    published = ma_fields.Bool(missing=False)

    @validates('tags')
    def validate_tags_unique(self, value):
        if value and len(value) != len(set(value)):
            raise ValidationError('Tags must be unique')

class CommentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    author_name = ma_fields.Str(required=True, validate=Length(min=2, max=50))
    author_email = ma_fields.Email(required=True)
    text = ma_fields.Str(required=True, validate=Length(min=1, max=1000))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_slug(title):
    """Create URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50]

def paginate(query, page=1, per_page=10):
    """Paginate query results"""
    total = query.count()
    pages = (total + per_page - 1) // per_page
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages
        }
    }

# ============================================================================
# NAMESPACES
# ============================================================================

auth_ns = Namespace('auth', description='Authentication operations')
articles_ns = Namespace('articles', description='Article operations')
authors_ns = Namespace('authors', description='Author operations')

api.add_namespace(auth_ns, path='/auth')
api.add_namespace(articles_ns, path='/articles')
api.add_namespace(authors_ns, path='/authors')

# ============================================================================
# API MODELS (for Swagger documentation)
# ============================================================================

user_registration = auth_ns.model('UserRegistration', {
    'username': fields.String(required=True, description='Username (3-50 chars)'),
    'email': fields.String(required=True, description='Valid email'),
    'password': fields.String(required=True, description='Strong password'),
    'bio': fields.String(description='User bio (max 500 chars)')
})

user_login = auth_ns.model('UserLogin', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password')
})

article_create = articles_ns.model('ArticleCreate', {
    'title': fields.String(required=True, description='Title (5-200 chars)'),
    'content': fields.String(required=True, description='Content (50+ chars)'),
    'category': fields.String(description='Category'),
    'tags': fields.List(fields.String, description='Tags (max 10)'),
    'published': fields.Boolean(description='Published status')
})

comment_create = api.model('CommentCreate', {
    'author_name': fields.String(required=True, description='Name'),
    'author_email': fields.String(required=True, description='Email'),
    'text': fields.String(required=True, description='Comment text')
})

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@auth_ns.route('/register')
class UserRegister(Resource):
    @auth_ns.expect(user_registration)
    def post(self):
        """Register new user"""
        schema = UserRegistrationSchema()

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        user = User(
            username=data['username'],
            email=data['email'],
            bio=data.get('bio')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return {
            'message': 'User registered successfully',
            'user': user.to_dict()
        }, 201

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(user_login)
    def post(self):
        """Login and get JWT token"""
        schema = UserLoginSchema()

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid email or password'}, 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, 200

@auth_ns.route('/me')
class CurrentUser(Resource):
    @jwt_required()
    def get(self):
        """Get current user info"""
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return user.to_dict(), 200

@auth_ns.route('/logout')
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        """Logout (blacklist token)"""
        jti = get_jwt()['jti']
        blacklisted = TokenBlacklist(jti=jti)
        db.session.add(blacklisted)
        db.session.commit()
        return {'message': 'Logged out successfully'}, 200

# ============================================================================
# ARTICLE ROUTES
# ============================================================================

@articles_ns.route('/')
class ArticleList(Resource):
    def get(self):
        """Get articles with optional filters"""
        # Query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        search = request.args.get('search')
        category = request.args.get('category')
        published = request.args.get('published')

        # Build query
        query = Article.query

        if search:
            query = query.filter(
                db.or_(
                    Article.title.ilike(f'%{search}%'),
                    Article.content.ilike(f'%{search}%')
                )
            )

        if category:
            query = query.filter_by(category=category)

        if published is not None:
            published_bool = published.lower() == 'true'
            query = query.filter_by(published=published_bool)

        # Order by newest first
        query = query.order_by(Article.created_at.desc())

        # Paginate
        result = paginate(query, page, per_page)

        return {
            'articles': [article.to_dict() for article in result['items']],
            'pagination': result['pagination']
        }, 200

    @jwt_required()
    @articles_ns.expect(article_create)
    def post(self):
        """Create new article (requires auth)"""
        user_id = get_jwt_identity()
        schema = ArticleSchema()

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        # Create slug
        slug = create_slug(data['title'])

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Article.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        article = Article(
            title=data['title'],
            content=data['content'],
            slug=slug,
            author_id=user_id,
            category=data.get('category'),
            tags=data.get('tags', []),
            published=data.get('published', False)
        )

        db.session.add(article)
        db.session.commit()

        return article.to_dict(), 201

@articles_ns.route('/<int:article_id>')
class ArticleItem(Resource):
    def get(self, article_id):
        """Get single article"""
        article = Article.query.get_or_404(article_id)

        # Increment view count
        article.views += 1
        db.session.commit()

        return article.to_dict(include_comments=True), 200

    @jwt_required()
    @articles_ns.expect(article_create)
    def put(self, article_id):
        """Update article (requires auth and ownership)"""
        user_id = get_jwt_identity()
        article = Article.query.get_or_404(article_id)

        if article.author_id != user_id:
            return {'message': 'Not authorized'}, 403

        schema = ArticleSchema()

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        # Update fields
        article.title = data['title']
        article.content = data['content']
        article.category = data.get('category')
        article.tags = data.get('tags', [])
        article.published = data.get('published', False)

        # Update slug if title changed
        if data['title'] != article.title:
            article.slug = create_slug(data['title'])

        db.session.commit()

        return article.to_dict(), 200

    @jwt_required()
    def delete(self, article_id):
        """Delete article (requires auth and ownership)"""
        user_id = get_jwt_identity()
        article = Article.query.get_or_404(article_id)

        if article.author_id != user_id:
            return {'message': 'Not authorized'}, 403

        db.session.delete(article)
        db.session.commit()

        return {'message': 'Article deleted'}, 204

@articles_ns.route('/<int:article_id>/comments')
class ArticleComments(Resource):
    def get(self, article_id):
        """Get comments for article"""
        article = Article.query.get_or_404(article_id)
        comments = Comment.query.filter_by(article_id=article_id).order_by(Comment.created_at.desc()).all()

        return {
            'comments': [c.to_dict() for c in comments]
        }, 200

    @articles_ns.expect(comment_create)
    def post(self, article_id):
        """Add comment to article"""
        article = Article.query.get_or_404(article_id)
        schema = CommentSchema()

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        comment = Comment(
            article_id=article_id,
            author_name=data['author_name'],
            author_email=data['author_email'],
            text=data['text']
        )

        db.session.add(comment)
        db.session.commit()

        return comment.to_dict(), 201

@articles_ns.route('/<int:article_id>/image')
class ArticleImage(Resource):
    @jwt_required()
    def post(self, article_id):
        """Upload image for article"""
        user_id = get_jwt_identity()
        article = Article.query.get_or_404(article_id)

        if article.author_id != user_id:
            return {'message': 'Not authorized'}, 403

        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400

        file = request.files['file']

        # Validate file
        if file.filename == '':
            return {'error': 'No file selected'}, 400

        # Check size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > 5 * 1024 * 1024:
            return {'error': 'File too large (max 5MB)'}, 400

        # Check extension
        filename = secure_filename(file.filename)
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return {'error': 'Invalid file type. Allowed: jpg, png, gif'}, 400

        # Verify it's actually an image
        try:
            img = Image.open(file)
            img.verify()
            file.seek(0)
        except Exception:
            return {'error': 'Invalid image file'}, 400

        # Save file
        unique_filename = f"article_{article_id}_{uuid.uuid4().hex[:8]}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # Update article
        article.image_url = f'/uploads/{unique_filename}'
        db.session.commit()

        return {
            'message': 'Image uploaded',
            'image_url': article.image_url
        }, 200

# ============================================================================
# AUTHOR ROUTES
# ============================================================================

@authors_ns.route('/')
class AuthorList(Resource):
    def get(self):
        """Get all authors"""
        authors = User.query.all()
        return {'authors': [author.to_dict() for author in authors]}, 200

@authors_ns.route('/<int:author_id>')
class AuthorItem(Resource):
    def get(self, author_id):
        """Get author details"""
        author = User.query.get_or_404(author_id)
        return author.to_dict(), 200

@authors_ns.route('/<int:author_id>/articles')
class AuthorArticles(Resource):
    def get(self, author_id):
        """Get author's articles"""
        author = User.query.get_or_404(author_id)
        articles = Article.query.filter_by(author_id=author_id).order_by(Article.created_at.desc()).all()

        return {
            'author': author.to_dict(),
            'articles': [article.to_dict(include_author=False) for article in articles]
        }, 200

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

with app.app_context():
    db.create_all()
    print("✅ Database tables created!")
    print("📊 Tables: users_frontend, articles_frontend, comments_frontend, token_blacklist_frontend")

    # Create sample data if database is empty
    if User.query.count() == 0:
        print("📝 Creating sample data...")

        # Sample users
        user1 = User(username='johndoe', email='john@example.com', bio='Tech enthusiast')
        user1.set_password('Password123!')

        user2 = User(username='janedoe', email='jane@example.com', bio='Science writer')
        user2.set_password('Password123!')

        db.session.add_all([user1, user2])
        db.session.commit()

        # Sample articles
        article1 = Article(
            title='Introduction to Streamlit',
            content='Streamlit is an amazing framework for building data applications with Python. ' * 5,
            slug='introduction-to-streamlit',
            author_id=user1.id,
            category='Technology',
            tags=['python', 'streamlit', 'tutorial'],
            published=True,
            views=42
        )

        article2 = Article(
            title='Flask REST API Best Practices',
            content='Building REST APIs with Flask requires following certain best practices. ' * 5,
            slug='flask-rest-api-best-practices',
            author_id=user1.id,
            category='Technology',
            tags=['python', 'flask', 'api'],
            published=True,
            views=87
        )

        article3 = Article(
            title='Understanding Climate Change',
            content='Climate change is one of the most pressing issues of our time. ' * 5,
            slug='understanding-climate-change',
            author_id=user2.id,
            category='Science',
            tags=['climate', 'environment'],
            published=True,
            views=156
        )

        db.session.add_all([article1, article2, article3])
        db.session.commit()

        # Sample comments
        comment1 = Comment(
            article_id=article1.id,
            author_name='Alice',
            author_email='alice@example.com',
            text='Great introduction! Very helpful.'
        )

        comment2 = Comment(
            article_id=article1.id,
            author_name='Bob',
            author_email='bob@example.com',
            text='Thanks for sharing this tutorial!'
        )

        db.session.add_all([comment1, comment2])
        db.session.commit()

        print("✅ Sample data created!")
        print(f"   Users: {User.query.count()}")
        print(f"   Articles: {Article.query.count()}")
        print(f"   Comments: {Comment.query.count()}")

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 UNIFIED BACKEND API FOR STREAMLIT FRONTEND")
    print("="*70)
    print("📖 Chapter 6: Frontend Development with Streamlit")
    print()
    print("Features:")
    print("  ✅ RESTful API design")
    print("  ✅ JWT authentication")
    print("  ✅ Data validation with Marshmallow")
    print("  ✅ Database integration")
    print("  ✅ File upload support")
    print("  ✅ CORS enabled for frontend")
    print()
    print("📡 API Base URL: http://localhost:5000/api")
    print("📡 Swagger UI: http://localhost:5000/swagger")
    print()
    print("Sample credentials:")
    print("  Email: john@example.com")
    print("  Password: Password123!")
    print()
    print("="*70 + "\n")

    app.run(debug=True, port=5000, host='0.0.0.0')
