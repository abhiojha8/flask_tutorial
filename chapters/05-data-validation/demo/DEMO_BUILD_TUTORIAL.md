# Building the Validation Demo - Step-by-Step Tutorial

This tutorial shows the progressive steps to build the validation demo app.
Use these as teaching checkpoints during live coding.

---

## STEP 1: Project Setup & Basic Flask App

**What we're building:** Flask app with database connection

```
PROJECT STRUCTURE:
validation_demo/
  ├── app.py
  ├── .env
  └── requirements.txt

INSTALL:
pip install flask flask-restx flask-sqlalchemy marshmallow python-dotenv psycopg2-binary

.env FILE:
DATABASE_URL="postgresql://..."
```

**Code checkpoint:**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()
    print("✅ Database connected!")

if __name__ == '__main__':
    app.run(debug=True)
```

**Test:** Run and see "Database connected!"

---

## STEP 2: User Model

**What we're adding:** Database model for users

```python
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users_validation'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age
        }
```

---

## STEP 3: Basic Marshmallow Schema

**What we're adding:** First validation schema

```python
from marshmallow import Schema, fields as ma_fields, ValidationError
from marshmallow.validate import Length, Range, Email as EmailValidator

class UserSchema(Schema):
    username = ma_fields.Str(
        required=True,
        validate=Length(min=3, max=50)
    )
    email = ma_fields.Email(required=True)
    age = ma_fields.Int(
        required=True,
        validate=Range(min=13, max=120)
    )
```

**Test in Python shell:**
```python
schema = UserSchema()

# Valid data
data = schema.load({'username': 'john', 'email': 'john@ex.com', 'age': 25})
print(data)  # Success!

# Invalid data
try:
    schema.load({'username': 'ab', 'email': 'invalid', 'age': 10})
except ValidationError as err:
    print(err.messages)
    # {'username': ['Length must be between 3 and 50.'],
    #  'email': ['Not a valid email address.'],
    #  'age': ['Must be greater than or equal to 13.']}
```

---

## STEP 4: Flask-RESTX Setup

**What we're adding:** API with Swagger

```python
from flask_restx import Api, Namespace, Resource, fields

api = Api(
    app,
    title='Validation Demo',
    description='Marshmallow validation examples',
    doc='/swagger'
)

users_ns = Namespace('users', description='User operations')
api.add_namespace(users_ns, path='/users')
```

**Test:** Open http://localhost:5000/swagger

---

## STEP 5: Registration Endpoint with Validation

**What we're adding:** Validated user registration

```python
user_model = users_ns.model('User', {
    'username': fields.String(required=True, description='3-50 characters'),
    'email': fields.String(required=True, description='Valid email'),
    'age': fields.Integer(required=True, description='13-120')
})

@users_ns.route('/register')
class UserRegister(Resource):
    @users_ns.expect(user_model)
    def post(self):
        schema = UserSchema()

        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        user = User(
            username=data['username'],
            email=data['email'],
            age=data['age']
        )
        db.session.add(user)
        db.session.commit()

        return {'message': 'User registered', 'user': user.to_dict()}, 201
```

**Test in Swagger:**
- Try `{"username": "ab", "email": "invalid", "age": 10}` → See 400 with errors
- Try valid data → 201 success

---

## STEP 6: Custom Password Validator

**What we're adding:** Password strength checking

```python
import re

def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters')

    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain uppercase letter')

    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain lowercase letter')

    if not re.search(r'\d', password):
        raise ValidationError('Password must contain a number')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain special character')

# Add to schema
class UserSchema(Schema):
    # ... existing fields ...
    password = ma_fields.Str(required=True)

    @validates('password')
    def validate_password(self, value):
        validate_password_strength(value)
```

**Test:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "age": 25,
  "password": "weak"
}
```
Expected: Multiple password errors!

---

## STEP 7: Username Blacklist Validator

**What we're adding:** Reserved username checking

```python
class UserSchema(Schema):
    # ... fields ...

    @validates('username')
    def validate_username(self, value):
        # Reserved names
        reserved = ['admin', 'root', 'system', 'moderator']
        if value.lower() in reserved:
            raise ValidationError(f'Username "{value}" is reserved')

        # Must start with letter
        if not value[0].isalpha():
            raise ValidationError('Username must start with a letter')

        # Check if exists
        if User.query.filter_by(username=value).first():
            raise ValidationError('Username already exists')
```

**Test:**
- Username "admin" → Reserved error
- Username "123test" → Must start with letter
- Register twice → Already exists error

---

## STEP 8: Nested Address Validation

**What we're adding:** Address as nested object

```python
class AddressSchema(Schema):
    street = ma_fields.Str(required=True, validate=Length(max=200))
    city = ma_fields.Str(required=True, validate=Length(max=100))
    zip_code = ma_fields.Str(required=True)

    @validates('zip_code')
    def validate_zip(self, value):
        if not re.match(r'^\d{5}$', value):
            raise ValidationError('Zip code must be exactly 5 digits')

class UserWithAddressSchema(Schema):
    username = ma_fields.Str(required=True, validate=Length(min=3, max=50))
    email = ma_fields.Email(required=True)
    address = ma_fields.Nested(AddressSchema, required=True)
```

**Test:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "address": {
    "street": "123 Main St",
    "city": "Boston",
    "zip_code": "ABC"
  }
}
```
Expected: `{"address": {"zip_code": ["Zip code must be exactly 5 digits"]}}`

---

## STEP 9: Post Model with Comments

**What we're adding:** List validation

```python
class Post(db.Model):
    __tablename__ = 'posts_validation'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Comment(db.Model):
    __tablename__ = 'comments_validation'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts_validation.id'))
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)

# Schemas
class CommentSchema(Schema):
    text = ma_fields.Str(required=True, validate=Length(min=1, max=1000))
    author = ma_fields.Str(required=True, validate=Length(min=2, max=50))

class PostSchema(Schema):
    title = ma_fields.Str(required=True, validate=Length(min=5, max=200))
    content = ma_fields.Str(required=True, validate=Length(min=10))
    comments = ma_fields.List(ma_fields.Nested(CommentSchema))
```

**Test:**
```json
{
  "title": "My Post",
  "content": "Great content here",
  "comments": [
    {"text": "Good!", "author": "Alice"},
    {"text": "", "author": "Bob"}
  ]
}
```
Expected: Error on comment index 1

---

## STEP 10: Cross-Field Validation

**What we're adding:** Event with date validation

```python
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events_validation'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

class EventSchema(Schema):
    title = ma_fields.Str(required=True, validate=Length(min=5, max=200))
    start_date = ma_fields.DateTime(required=True)
    end_date = ma_fields.DateTime(required=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data['end_date'] <= data['start_date']:
            raise ValidationError(
                'End date must be after start date',
                field_name='end_date'
            )

        if data['start_date'] < datetime.utcnow():
            raise ValidationError(
                'Start date cannot be in the past',
                field_name='start_date'
            )
```

**Test:**
```json
{
  "title": "Conference",
  "start_date": "2025-01-15T09:00:00",
  "end_date": "2025-01-10T17:00:00"
}
```
Expected: End date error

---

## STEP 11: Context-Aware Validation (Quota)

**What we're adding:** Daily post limit per user

```python
class PostSchema(Schema):
    title = ma_fields.Str(required=True)
    content = ma_fields.Str(required=True)

    @validates_schema
    def check_quota(self, data, **kwargs):
        user_id = self.context.get('user_id')
        if not user_id:
            return

        # Count today's posts
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
        count = Post.query.filter(
            Post.author_id == user_id,
            Post.created_at >= today_start
        ).count()

        if count >= 5:
            raise ValidationError(
                'Daily quota exceeded (max 5 posts/day)',
                field_name='_quota'
            )

# Usage in endpoint
schema = PostSchema(context={'user_id': current_user.id})
```

**Test:** Create 6 posts in one day → 6th fails

---

## STEP 12: File Upload Validation

**What we're adding:** Image upload with validation

```python
from werkzeug.utils import secure_filename
from PIL import Image
import os

def validate_image(file):
    # Size check
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > 5 * 1024 * 1024:
        raise ValidationError('File too large (max 5MB)')

    # Extension check
    filename = secure_filename(file.filename)
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        raise ValidationError('Invalid file type')

    # Verify actual image
    try:
        img = Image.open(file)
        if img.width > 2000 or img.height > 2000:
            raise ValidationError('Image too large (max 2000x2000)')
    except Exception:
        raise ValidationError('Invalid image file')
    finally:
        file.seek(0)

# Endpoint
@posts_ns.route('/<int:post_id>/image')
class PostImage(Resource):
    def post(self, post_id):
        if 'file' not in request.files:
            return {'error': 'No file provided'}, 400

        file = request.files['file']

        try:
            validate_image(file)
        except ValidationError as err:
            return {'error': str(err)}, 400

        # Save file...
        return {'message': 'Image uploaded'}, 200
```

---

## Complete Flow Testing

1. **Register User** → POST /users/register with validation
2. **Create Post** → Validates title, content
3. **Add Comments** → List validation
4. **Create Event** → Cross-field date validation
5. **Upload Image** → File validation
6. **Hit Quota** → Context-aware validation

---

## Validation Checklist

✅ Field-level validation (Length, Range, Email)
✅ Custom validators (@validates)
✅ Password strength checking
✅ Reserved username blacklist
✅ Nested object validation
✅ List of objects validation
✅ Cross-field validation (@validates_schema)
✅ Context-aware validation (quota)
✅ File upload validation
✅ Error message formatting

---

## Security Best Practices Applied

1. ✅ Server-side validation (never trust client)
2. ✅ Input sanitization (secure_filename)
3. ✅ File type verification (MIME check)
4. ✅ Rate limiting (quota validation)
5. ✅ SQL injection prevention (parameterized queries + validation)
6. ✅ XSS prevention (validate input format)
7. ✅ Clear error messages (without exposing system details)

---

## Next Steps

- Add more complex validators (phone, credit card, etc.)
- Implement custom error message formatting
- Add request ID tracking in errors
- Create reusable validator library
- Add validation middleware
- Implement field-level sanitization
- Add schema versioning for API evolution

---

**Teaching Tip:** Build this incrementally! Don't show the complete app at once. Each step should work and be testable before moving to the next.
