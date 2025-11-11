"""
Exercise 5: Complex Business Rules
Chapter 5: Data Validation & Error Handling

Learning Objectives:
- Implement cross-field validation with @validates_schema
- Build context-aware validators
- Implement quota and rate limiting validation
- Create conditional required fields
- Validate business logic constraints

TODO: Complete the marked sections to implement business rule validation!
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from marshmallow import Schema, fields as ma_fields, validates, validates_schema, ValidationError, EXCLUDE
from marshmallow.validate import Length, Range, OneOf
from datetime import datetime, timedelta
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
    title='Exercise 5: Business Rules',
    description='Learn to implement complex business logic validation',
    doc='/swagger'
)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    __tablename__ = 'users_ex5'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)
    events = db.relationship('Event', backref='organizer', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}

class Post(db.Model):
    __tablename__ = 'posts_ex5'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    tags = db.Column(db.JSON, default=list)
    status = db.Column(db.String(20), default='draft')  # draft, published
    author_id = db.Column(db.Integer, db.ForeignKey('users_ex5.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags or [],
            'status': self.status,
            'author_id': self.author_id
        }

class Event(db.Model):
    __tablename__ = 'events_ex5'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users_ex5.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'organizer_id': self.organizer_id
        }

class Product(db.Model):
    __tablename__ = 'products_ex5'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    regular_price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'regular_price': self.regular_price,
            'discount_price': self.discount_price
        }

# ============================================================================
# TODO 1: Create EventSchema with Cross-Field Validation
# ============================================================================
# Create a schema that validates:
# - title: Required, 5-200 chars
# - start_date: Required datetime
# - end_date: Required datetime
# - Business rule: end_date must be after start_date
#
# Hints:
# - Use @validates_schema decorator for cross-field validation
# - Access fields with data['field_name']
# - Compare datetime objects directly

class EventSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define fields
    # title = ma_fields.Str(required=True, validate=Length(min=5, max=200))
    # start_date = ma_fields.DateTime(required=True)
    # end_date = ma_fields.DateTime(required=True)

    # TODO: Add @validates_schema to check date logic
    # @validates_schema
    # def validate_dates(self, data, **kwargs):
    #     """Ensure end_date is after start_date"""
    #     if data['end_date'] <= data['start_date']:
    #         raise ValidationError(
    #             'End date must be after start date',
    #             field_name='end_date'
    #         )
    #
    #     # Also check that start_date is not in the past
    #     if data['start_date'] < datetime.utcnow():
    #         raise ValidationError(
    #             'Start date cannot be in the past',
    #             field_name='start_date'
    #         )

    pass

# ============================================================================
# TODO 2: Create PostSchema with Quota Validation
# ============================================================================
# Create a schema with context-aware validation:
# - title: Required, 5-200 chars
# - content: Conditionally required (required if status='published')
# - tags: List of strings, must be unique within user's posts
# - status: 'draft' or 'published'
# - Business rules:
#   1. User can create max 5 posts per day
#   2. Tags must not duplicate across user's existing posts
#   3. If status='published', content is required
#
# Hints:
# - Use self.context.get('user_id') to get user from context
# - Query database within validator
# - Use @validates_schema for multi-field logic

class PostSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define fields
    # title = ma_fields.Str(required=True, validate=Length(min=5, max=200))
    # content = ma_fields.Str(required=False, allow_none=True)
    # tags = ma_fields.List(ma_fields.Str(), validate=Length(max=5))
    # status = ma_fields.Str(validate=OneOf(['draft', 'published']))

    # TODO: Validate tags uniqueness across user's posts
    # @validates('tags')
    # def validate_tags_unique(self, value):
    #     """Ensure tags are unique across user's posts"""
    #     if not value:
    #         return
    #
    #     user_id = self.context.get('user_id')
    #     if not user_id:
    #         return
    #
    #     # Get all tags from user's existing posts
    #     user_posts = Post.query.filter_by(author_id=user_id).all()
    #     existing_tags = set()
    #     for post in user_posts:
    #         if post.tags:
    #             existing_tags.update(post.tags)
    #
    #     # Check for duplicates
    #     for tag in value:
    #         if tag in existing_tags:
    #             raise ValidationError(f'Tag "{tag}" already used in another post')

    # TODO: Validate daily quota
    # @validates_schema
    # def validate_quota(self, data, **kwargs):
    #     """Check if user has exceeded daily post quota"""
    #     user_id = self.context.get('user_id')
    #     if not user_id:
    #         return
    #
    #     # Count posts created today
    #     today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    #     today_posts = Post.query.filter(
    #         Post.author_id == user_id,
    #         Post.created_at >= today_start
    #     ).count()
    #
    #     max_daily_posts = 5
    #     if today_posts >= max_daily_posts:
    #         raise ValidationError(
    #             f'Daily post quota exceeded. Maximum {max_daily_posts} posts per day.',
    #             field_name='_quota'
    #         )

    # TODO: Validate conditional content requirement
    # @validates_schema
    # def validate_published_requirements(self, data, **kwargs):
    #     """If status is published, content must be provided"""
    #     if data.get('status') == 'published':
    #         if not data.get('content') or len(data.get('content', '').strip()) < 10:
    #             raise ValidationError(
    #                 'Content (min 10 chars) is required when publishing',
    #                 field_name='content'
    #             )

    pass

# ============================================================================
# TODO 3: Create ProductSchema with Price Validation
# ============================================================================
# Create a schema that validates:
# - name: Required, 3-200 chars
# - regular_price: Required, min 0.01
# - discount_price: Optional
# - Business rule: discount_price must be less than regular_price
#
# Hints:
# - Use @validates_schema for price comparison
# - Check if discount_price exists before comparing

class ProductSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    # TODO: Define fields
    # name = ma_fields.Str(required=True, validate=Length(min=3, max=200))
    # regular_price = ma_fields.Float(required=True, validate=Range(min=0.01))
    # discount_price = ma_fields.Float(required=False, allow_none=True)

    # TODO: Validate price logic
    # @validates_schema
    # def validate_prices(self, data, **kwargs):
    #     """Ensure discount is less than regular price"""
    #     if data.get('discount_price') is not None:
    #         if data['discount_price'] >= data['regular_price']:
    #             raise ValidationError(
    #                 'Discount price must be less than regular price',
    #                 field_name='discount_price'
    #             )
    #
    #         if data['discount_price'] < 0:
    #             raise ValidationError(
    #                 'Discount price cannot be negative',
    #                 field_name='discount_price'
    #             )

    pass

# ============================================================================
# NAMESPACES & MODELS
# ============================================================================

events_ns = Namespace('events', description='Event operations')
posts_ns = Namespace('posts', description='Post operations')
products_ns = Namespace('products', description='Product operations')

api.add_namespace(events_ns, path='/events')
api.add_namespace(posts_ns, path='/posts')
api.add_namespace(products_ns, path='/products')

event_model = events_ns.model('Event', {
    'title': fields.String(required=True),
    'start_date': fields.DateTime(required=True),
    'end_date': fields.DateTime(required=True)
})

post_model = posts_ns.model('Post', {
    'title': fields.String(required=True),
    'content': fields.String(description='Required if status=published'),
    'tags': fields.List(fields.String, description='Must be unique across your posts'),
    'status': fields.String(description='draft or published')
})

product_model = products_ns.model('Product', {
    'name': fields.String(required=True),
    'regular_price': fields.Float(required=True),
    'discount_price': fields.Float(description='Must be less than regular price')
})

# ============================================================================
# TODO 4: Implement Event Creation with Date Validation
# ============================================================================

@events_ns.route('/')
class EventList(Resource):
    @events_ns.expect(event_model)
    def post(self):
        """Create event with date validation"""

        # TODO: Validate with EventSchema
        # schema = EventSchema()
        #
        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return {'errors': err.messages}, 400

        # TODO: Create event (use first user for demo)
        # user = User.query.first()
        # if not user:
        #     # Create a demo user
        #     user = User(username='demo', email='demo@example.com')
        #     db.session.add(user)
        #     db.session.flush()
        #
        # event = Event(
        #     title=data['title'],
        #     start_date=data['start_date'],
        #     end_date=data['end_date'],
        #     organizer_id=user.id
        # )
        # db.session.add(event)
        # db.session.commit()

        # TODO: Return success
        # return {'message': 'Event created', 'event': event.to_dict()}, 201

        return {'error': 'Not implemented. Complete TODO 4!'}, 501

    def get(self):
        """Get all events"""
        events = Event.query.all()
        return {'events': [e.to_dict() for e in events]}, 200

# ============================================================================
# TODO 5: Implement Post Creation with Quota Validation
# ============================================================================

@posts_ns.route('/')
class PostList(Resource):
    @posts_ns.expect(post_model)
    def post(self):
        """Create post with quota and tag validation"""

        # TODO: Get or create user
        # user = User.query.first()
        # if not user:
        #     user = User(username='demo', email='demo@example.com')
        #     db.session.add(user)
        #     db.session.flush()

        # TODO: Validate with PostSchema (pass user_id in context)
        # schema = PostSchema(context={'user_id': user.id})
        #
        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return {'errors': err.messages}, 400

        # TODO: Create post
        # post = Post(
        #     title=data['title'],
        #     content=data.get('content'),
        #     tags=data.get('tags', []),
        #     status=data.get('status', 'draft'),
        #     author_id=user.id
        # )
        # db.session.add(post)
        # db.session.commit()

        # TODO: Return success
        # return {'message': 'Post created', 'post': post.to_dict()}, 201

        return {'error': 'Not implemented. Complete TODO 5!'}, 501

    def get(self):
        """Get all posts"""
        posts = Post.query.all()
        return {'posts': [p.to_dict() for p in posts]}, 200

# ============================================================================
# TODO 6: Implement Product Creation with Price Validation
# ============================================================================

@products_ns.route('/')
class ProductList(Resource):
    @products_ns.expect(product_model)
    def post(self):
        """Create product with price validation"""

        # TODO: Validate with ProductSchema
        # schema = ProductSchema()
        #
        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return {'errors': err.messages}, 400

        # TODO: Create product
        # product = Product(
        #     name=data['name'],
        #     regular_price=data['regular_price'],
        #     discount_price=data.get('discount_price')
        # )
        # db.session.add(product)
        # db.session.commit()

        # TODO: Return success
        # return {'message': 'Product created', 'product': product.to_dict()}, 201

        return {'error': 'Not implemented. Complete TODO 6!'}, 501

    def get(self):
        """Get all products"""
        products = Product.query.all()
        return {'products': [p.to_dict() for p in products]}, 200

# ============================================================================
# DATABASE INIT
# ============================================================================

with app.app_context():
    db.create_all()
    print("✅ Database tables created: users_ex5, posts_ex5, events_ex5, products_ex5")

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎯 EXERCISE 5: Complex Business Rules")
    print("="*70)
    print("\nTODO List:")
    print("  1. Create EventSchema with date cross-validation")
    print("  2. Create PostSchema with quota & tag uniqueness validation")
    print("  3. Create ProductSchema with price validation")
    print("  4. Implement event creation endpoint")
    print("  5. Implement post creation endpoint with context")
    print("  6. Implement product creation endpoint")
    print("\nTest Cases:")
    print("  ✓ Event with end_date before start_date → Error")
    print("  ✓ Create 6th post in one day → Quota exceeded")
    print("  ✓ Post with duplicate tag → Tag already used error")
    print("  ✓ Publish post without content → Content required error")
    print("  ✓ Product with discount > regular price → Error")
    print("  ✓ Valid data → Success!")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
