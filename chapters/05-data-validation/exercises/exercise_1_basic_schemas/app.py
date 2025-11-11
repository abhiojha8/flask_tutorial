"""
Exercise 1: Basic Marshmallow Schemas
Chapter 5: Data Validation & Error Handling

Learning Objectives:
- Define Marshmallow schemas with typed fields
- Use built-in validators (Length, Range, Email)
- Handle ValidationError exceptions
- Return user-friendly error messages

TODO: Complete the marked sections to implement basic schema validation!
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from marshmallow import Schema, fields as ma_fields, ValidationError, EXCLUDE
from marshmallow.validate import Length, Range, Email as EmailValidator, OneOf
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api = Api(
    app,
    version='1.0',
    title='Exercise 1: Basic Schemas',
    description='Learn Marshmallow schema validation with built-in validators',
    doc='/swagger'
)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    __tablename__ = 'users_ex1'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'bio': self.bio
        }

class Post(db.Model):
    __tablename__ = 'posts_ex1'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'rating': self.rating
        }

# ============================================================================
# TODO 1: Create UserSchema with Field Validators
# ============================================================================
# Create a Marshmallow schema for user registration with these validations:
# - username: Required string, 3-50 characters
# - email: Required email format
# - age: Required integer, 13-120 range
# - bio: Optional string, max 500 characters
#
# Hints:
# - Use ma_fields.Str(), ma_fields.Email(), ma_fields.Int()
# - Use validate=Length(min=X, max=Y) for string length
# - Use validate=Range(min=X, max=Y) for numbers
# - Use required=True for mandatory fields
# - Use required=False or missing=None for optional fields

class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields

    # TODO: Define username field (required, 3-50 chars)
    # username = ...

    # TODO: Define email field (required, valid email)
    # email = ...

    # TODO: Define age field (required, 13-120 range)
    # age = ...

    # TODO: Define bio field (optional, max 500 chars)
    # bio = ...
    pass

# ============================================================================
# TODO 2: Create PostSchema with Validators
# ============================================================================
# Create a schema for post creation with:
# - title: Required string, 5-200 characters
# - content: Required string, minimum 10 characters
# - category: Required string, one of ['technology', 'sports', 'entertainment', 'business']
# - rating: Optional integer, 1-5 range
#
# Hints:
# - Use OneOf(['option1', 'option2']) for enum validation
# - Use validate=Length(min=X) for minimum length without max

class PostSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define title field (required, 5-200 chars)
    # title = ...

    # TODO: Define content field (required, min 10 chars)
    # content = ...

    # TODO: Define category field (required, one of the allowed values)
    # category = ...

    # TODO: Define rating field (optional, 1-5 range)
    # rating = ...
    pass

# ============================================================================
# NAMESPACES & MODELS
# ============================================================================

users_ns = Namespace('users', description='User operations')
posts_ns = Namespace('posts', description='Post operations')

api.add_namespace(users_ns, path='/users')
api.add_namespace(posts_ns, path='/posts')

user_model = users_ns.model('User', {
    'username': fields.String(required=True, description='Username (3-50 chars)'),
    'email': fields.String(required=True, description='Valid email address'),
    'age': fields.Integer(required=True, description='Age (13-120)'),
    'bio': fields.String(description='Bio (max 500 chars)')
})

post_model = posts_ns.model('Post', {
    'title': fields.String(required=True, description='Title (5-200 chars)'),
    'content': fields.String(required=True, description='Content (min 10 chars)'),
    'category': fields.String(required=True, description='Category: technology, sports, entertainment, business'),
    'rating': fields.Integer(description='Rating (1-5)')
})

# ============================================================================
# TODO 3: Implement User Registration with Validation
# ============================================================================

@users_ns.route('/register')
class UserRegister(Resource):
    @users_ns.expect(user_model)
    def post(self):
        """Register new user with schema validation"""

        # TODO: Create schema instance
        # schema = UserSchema()

        # TODO: Validate request data using try/except
        # Hint: Use schema.load(request.json) inside try block
        # Catch ValidationError and return {'errors': err.messages}, 400

        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return ..., 400

        # TODO: After validation passes, create user
        # user = User(
        #     username=data['username'],
        #     email=data['email'],
        #     age=data['age'],
        #     bio=data.get('bio')
        # )
        # db.session.add(user)
        # db.session.commit()

        # TODO: Return success response
        # return {'message': 'User registered', 'user': user.to_dict()}, 201

        return {'error': 'Not implemented. Complete TODO 3!'}, 501

# ============================================================================
# TODO 4: Implement Post Creation with Validation
# ============================================================================

@posts_ns.route('/')
class PostList(Resource):
    @posts_ns.expect(post_model)
    def post(self):
        """Create new post with validation"""

        # TODO: Create PostSchema instance
        # schema = PostSchema()

        # TODO: Validate and load data
        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return {'errors': err.messages}, 400

        # TODO: Create post from validated data
        # post = Post(
        #     title=data['title'],
        #     content=data['content'],
        #     category=data['category'],
        #     rating=data.get('rating')
        # )
        # db.session.add(post)
        # db.session.commit()

        # TODO: Return success response
        # return {'message': 'Post created', 'post': post.to_dict()}, 201

        return {'error': 'Not implemented. Complete TODO 4!'}, 501

    def get(self):
        """Get all posts"""
        posts = Post.query.all()
        return {'posts': [p.to_dict() for p in posts]}, 200

@users_ns.route('/')
class UserList(Resource):
    def get(self):
        """Get all users"""
        users = User.query.all()
        return {'users': [u.to_dict() for u in users]}, 200

# ============================================================================
# DATABASE INIT
# ============================================================================

with app.app_context():
    db.create_all()
    print("✅ Database tables created: users_ex1, posts_ex1")

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📚 EXERCISE 1: Basic Marshmallow Schemas")
    print("="*70)
    print("\nTODO List:")
    print("  1. Create UserSchema with field validators")
    print("  2. Create PostSchema with OneOf validator")
    print("  3. Implement user registration with validation")
    print("  4. Implement post creation with validation")
    print("\nTest Cases:")
    print("  ✓ Register with username 'ab' → Should fail (too short)")
    print("  ✓ Register with invalid email → Should fail")
    print("  ✓ Register with age 10 → Should fail (too young)")
    print("  ✓ Create post with short title → Should fail")
    print("  ✓ Create post with invalid category → Should fail")
    print("  ✓ Valid data → Should succeed!")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
