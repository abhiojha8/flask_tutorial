"""
Exercise 3: Nested Validation
Chapter 5: Data Validation & Error Handling

Learning Objectives:
- Define nested schemas for complex objects
- Validate one-to-one relationships
- Validate one-to-many relationships (lists)
- Handle nested validation errors

TODO: Complete the marked sections to implement nested validation!
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from marshmallow import Schema, fields as ma_fields, validates, ValidationError, EXCLUDE
from marshmallow.validate import Length, Email as EmailValidator, OneOf
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api = Api(
    app,
    version='1.0',
    title='Exercise 3: Nested Validation',
    description='Learn to validate nested objects and relationships',
    doc='/swagger'
)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    __tablename__ = 'users_ex3'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Address fields (embedded)
    street = db.Column(db.String(200))
    city = db.Column(db.String(100))
    zip_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'address': {
                'street': self.street,
                'city': self.city,
                'zip_code': self.zip_code
            } if self.street else None
        }

class Post(db.Model):
    __tablename__ = 'posts_ex3'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users_ex3.id'), nullable=False)
    tags = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True)

    def to_dict(self, include_comments=False):
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'tags': self.tags or []
        }
        if include_comments:
            result['comments'] = [c.to_dict() for c in self.comments]
        return result

class Comment(db.Model):
    __tablename__ = 'comments_ex3'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts_ex3.id'), nullable=False)
    author_name = db.Column(db.String(50), nullable=False)
    author_email = db.Column(db.String(120), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'author': {
                'name': self.author_name,
                'email': self.author_email
            },
            'text': self.text
        }

# ============================================================================
# TODO 1: Create AddressSchema (for nested validation)
# ============================================================================
# Create a schema for address validation:
# - street: Required string, max 200 characters
# - city: Required string, max 100 characters
# - zip_code: Required string, exactly 5 digits (use regex validation)
#
# Hints:
# - Use @validates decorator for custom zip_code validation
# - Use re.match(r'^\d{5}$', value) to check for 5 digits

class AddressSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define street field (required, max 200 chars)
    # street = ma_fields.Str(required=True, validate=Length(max=200))

    # TODO: Define city field (required, max 100 chars)
    # city = ...

    # TODO: Define zip_code field (required)
    # zip_code = ma_fields.Str(required=True)

    # TODO: Add @validates('zip_code') to check format
    # @validates('zip_code')
    # def validate_zip(self, value):
    #     import re
    #     if not re.match(r'^\d{5}$', value):
    #         raise ValidationError('Zip code must be exactly 5 digits')

    pass

# ============================================================================
# TODO 2: Create UserSchema with Nested Address
# ============================================================================
# Create a schema that includes:
# - username: Required, 3-50 chars
# - email: Required, valid email
# - address: Nested AddressSchema, required
#
# Hints:
# - Use ma_fields.Nested(AddressSchema, required=True)

class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define username field
    # username = ma_fields.Str(required=True, validate=Length(min=3, max=50))

    # TODO: Define email field
    # email = ma_fields.Email(required=True)

    # TODO: Define address field (nested AddressSchema)
    # address = ma_fields.Nested(AddressSchema, required=True)

    pass

# ============================================================================
# TODO 3: Create CommentAuthorSchema (nested in comment)
# ============================================================================
# Create a schema for comment author info:
# - name: Required, 2-50 chars
# - email: Required, valid email

class CommentAuthorSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define name field
    # name = ma_fields.Str(required=True, validate=Length(min=2, max=50))

    # TODO: Define email field
    # email = ma_fields.Email(required=True)

    pass

# ============================================================================
# TODO 4: Create CommentSchema with Nested Author
# ============================================================================
# Create a schema for comments:
# - author: Nested CommentAuthorSchema, required
# - text: Required, 1-1000 chars

class CommentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define author field (nested)
    # author = ma_fields.Nested(CommentAuthorSchema, required=True)

    # TODO: Define text field
    # text = ma_fields.Str(required=True, validate=Length(min=1, max=1000))

    pass

# ============================================================================
# TODO 5: Create PostSchema with List of Comments
# ============================================================================
# Create a schema for posts:
# - title: Required, 5-200 chars
# - content: Required, min 10 chars
# - tags: List of strings, max 5 tags
# - comments: List of nested CommentSchema, optional
#
# Hints:
# - Use ma_fields.List(ma_fields.Str()) for list of strings
# - Use ma_fields.List(ma_fields.Nested(CommentSchema)) for list of objects

class PostSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define title field
    # title = ma_fields.Str(required=True, validate=Length(min=5, max=200))

    # TODO: Define content field
    # content = ma_fields.Str(required=True, validate=Length(min=10))

    # TODO: Define tags field (list of strings, max 5)
    # tags = ma_fields.List(ma_fields.Str(), validate=Length(max=5))

    # TODO: Define comments field (list of nested CommentSchema)
    # comments = ma_fields.List(ma_fields.Nested(CommentSchema), required=False)

    pass

# ============================================================================
# NAMESPACES & MODELS
# ============================================================================

users_ns = Namespace('users', description='User operations')
posts_ns = Namespace('posts', description='Post operations')

api.add_namespace(users_ns, path='/users')
api.add_namespace(posts_ns, path='/posts')

address_model = api.model('Address', {
    'street': fields.String(required=True),
    'city': fields.String(required=True),
    'zip_code': fields.String(required=True, description='5-digit zip code')
})

user_model = users_ns.model('UserWithAddress', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'address': fields.Nested(address_model, required=True)
})

comment_author_model = api.model('CommentAuthor', {
    'name': fields.String(required=True),
    'email': fields.String(required=True)
})

comment_model = api.model('Comment', {
    'author': fields.Nested(comment_author_model, required=True),
    'text': fields.String(required=True)
})

post_model = posts_ns.model('PostWithComments', {
    'title': fields.String(required=True),
    'content': fields.String(required=True),
    'tags': fields.List(fields.String, description='Max 5 tags'),
    'comments': fields.List(fields.Nested(comment_model))
})

# ============================================================================
# TODO 6: Implement User Registration with Nested Address
# ============================================================================

@users_ns.route('/register')
class UserRegister(Resource):
    @users_ns.expect(user_model)
    def post(self):
        """Register user with address validation"""

        # TODO: Validate with UserSchema
        # schema = UserSchema()
        #
        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return {'errors': err.messages}, 400

        # TODO: Create user with nested address data
        # user = User(
        #     username=data['username'],
        #     email=data['email'],
        #     street=data['address']['street'],
        #     city=data['address']['city'],
        #     zip_code=data['address']['zip_code']
        # )
        # db.session.add(user)
        # db.session.commit()

        # TODO: Return success
        # return {'message': 'User registered', 'user': user.to_dict()}, 201

        return {'error': 'Not implemented. Complete TODO 6!'}, 501

# ============================================================================
# TODO 7: Implement Post Creation with Nested Comments
# ============================================================================

@posts_ns.route('/')
class PostList(Resource):
    @posts_ns.expect(post_model)
    def post(self):
        """Create post with comments"""

        # TODO: Validate with PostSchema
        # schema = PostSchema()
        #
        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return {'errors': err.messages}, 400

        # TODO: Get or create author (use first user for demo)
        # author = User.query.first()
        # if not author:
        #     return {'error': 'No users found. Register a user first.'}, 400

        # TODO: Create post
        # post = Post(
        #     title=data['title'],
        #     content=data['content'],
        #     author_id=author.id,
        #     tags=data.get('tags', [])
        # )
        # db.session.add(post)
        # db.session.flush()  # Get post.id before adding comments

        # TODO: Create comments if provided
        # if 'comments' in data:
        #     for comment_data in data['comments']:
        #         comment = Comment(
        #             post_id=post.id,
        #             author_name=comment_data['author']['name'],
        #             author_email=comment_data['author']['email'],
        #             text=comment_data['text']
        #         )
        #         db.session.add(comment)

        # db.session.commit()

        # TODO: Return success
        # return {'message': 'Post created', 'post': post.to_dict(include_comments=True)}, 201

        return {'error': 'Not implemented. Complete TODO 7!'}, 501

    def get(self):
        """Get all posts"""
        posts = Post.query.all()
        return {'posts': [p.to_dict(include_comments=True) for p in posts]}, 200

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
    print("✅ Database tables created: users_ex3, posts_ex3, comments_ex3")

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏗️  EXERCISE 3: Nested Validation")
    print("="*70)
    print("\nTODO List:")
    print("  1. Create AddressSchema")
    print("  2. Create UserSchema with nested AddressSchema")
    print("  3. Create CommentAuthorSchema")
    print("  4. Create CommentSchema with nested CommentAuthorSchema")
    print("  5. Create PostSchema with list of nested CommentSchema")
    print("  6. Implement user registration with address")
    print("  7. Implement post creation with comments")
    print("\nTest Cases:")
    print("  ✓ Register with invalid zip_code → Nested field error")
    print("  ✓ Register with missing address fields → Nested required error")
    print("  ✓ Create post with invalid comment email → Nested list error")
    print("  ✓ Create post with empty comment text → Nested validation error")
    print("  ✓ Valid nested data → Success!")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
