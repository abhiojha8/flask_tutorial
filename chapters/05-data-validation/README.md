# Chapter 5: Data Validation & Error Handling

## 🎯 Chapter Goals

By the end of this chapter, you will:
- Master advanced input validation with Marshmallow
- Create custom validators for business rules
- Implement nested object validation
- Handle file upload validation
- Build comprehensive error handling
- Validate complex data structures
- Provide user-friendly error messages
- Implement data sanitization

## 📚 What You'll Learn

### Part 1: Validation Fundamentals
- Why validation matters (security & data integrity)
- Client-side vs Server-side validation
- Validation vs Sanitization
- Common validation patterns
- Error message design

### Part 2: Marshmallow Deep Dive
- What is Marshmallow?
- Schema definition and field types
- Built-in validators (Length, Range, Email, URL)
- Serialization vs Deserialization
- Schema nesting and relationships
- Pre/post processing hooks

### Part 3: Custom Validators
- Creating custom validation functions
- Using @validates decorator
- Cross-field validation
- Context-aware validation
- Reusable validator classes

### Part 4: Advanced Patterns
- File upload validation (size, type, content)
- Nested object validation
- List validation with nested schemas
- Conditional validation
- Business rule validation
- Error aggregation and formatting

## 🚀 Demo Project: Blog Platform with Advanced Validation

We'll add comprehensive validation to our blog platform:

**Features:**
- User registration with strict validation rules
- Post creation with content validation
- Comment validation with profanity filtering
- Image upload validation (size, format, dimensions)
- Tag validation with uniqueness checking
- Category validation with hierarchy
- Search input sanitization

**API Endpoints:**
```
POST   /users/register         - Register with validation
POST   /posts                  - Create post (title, content, tags)
PUT    /posts/{id}             - Update post (partial validation)
POST   /posts/{id}/images      - Upload image (file validation)
POST   /posts/{id}/comments    - Add comment (nested validation)
GET    /search                 - Search with sanitized input
```

## 💻 Exercises

### Exercise 1: Basic Marshmallow Schemas 🟢
**Topics:** Schema definition, field types, basic validators
- Create user registration schema
- Implement field-level validation
- Use built-in validators (Length, Email, Range)
- Return validation errors

### Exercise 2: Custom Validators 🟢
**Topics:** @validates decorator, custom logic, error messages
- Create password strength validator
- Implement username blacklist checking
- Build custom email domain validator
- Add phone number format validation

### Exercise 3: Nested Validation 🟡
**Topics:** Nested schemas, relationships, complex objects
- Validate post with embedded author
- Validate comment with nested user data
- Handle list of nested objects
- Implement recursive validation

### Exercise 4: File Upload Validation 🟡
**Topics:** File validation, MIME types, content checking
- Validate file size limits
- Check allowed file extensions
- Verify MIME types
- Validate image dimensions (PIL)
- Detect malicious files

### Exercise 5: Complex Business Rules 🔴
**Topics:** Cross-field validation, context validation, business logic
- Implement "end_date must be after start_date"
- Validate unique tags across posts
- Check user quota limits (max posts per day)
- Implement conditional required fields
- Build multi-step validation flows

## 🎓 Learning Path

```
1. Read: Validation concepts (theory)
   ↓
2. Demo: See Marshmallow in action
   ↓
3. Exercise 1: Basic schemas
   ↓
4. Exercise 2: Custom validators
   ↓
5. Exercise 3: Nested validation
   ↓
6. Exercise 4: File uploads
   ↓
7. Exercise 5: Business rules
```

## 📖 Key Concepts

### Why Validation Matters

**Security:**
```python
# ❌ Without validation
username = request.json['username']
# User sends: {"username": "<script>alert('XSS')</script>"}
# → Stored in DB, executed in browser!

# ✅ With validation
username = request.json['username']
if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
    return {'error': 'Invalid username'}, 400
```

**Data Integrity:**
```python
# ❌ Without validation
age = request.json['age']  # User sends: -5 or 999
# → Garbage data in database!

# ✅ With validation
schema = UserSchema()
data = schema.load(request.json)  # Raises ValidationError if invalid
```

### Marshmallow Basics

**Simple Schema:**
```python
from marshmallow import Schema, fields, validates, ValidationError

class UserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(required=True)

# Usage
schema = UserSchema()
data = schema.load({'username': 'john', 'email': 'john@example.com', 'age': 25})
# Returns validated data or raises ValidationError
```

**Field Validators:**
```python
from marshmallow.validate import Length, Range, OneOf

class UserSchema(Schema):
    username = fields.Str(
        required=True,
        validate=Length(min=3, max=20)
    )
    age = fields.Int(
        validate=Range(min=13, max=120)
    )
    role = fields.Str(
        validate=OneOf(['user', 'admin', 'moderator'])
    )
```

### Custom Validators

**Method-based:**
```python
class UserSchema(Schema):
    username = fields.Str(required=True)

    @validates('username')
    def validate_username(self, value):
        if value.lower() in ['admin', 'root', 'system']:
            raise ValidationError('Username is reserved')

        if not value[0].isalpha():
            raise ValidationError('Username must start with a letter')
```

**Function-based:**
```python
def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters')

    if not any(c.isupper() for c in password):
        raise ValidationError('Password must contain uppercase letter')

    if not any(c.isdigit() for c in password):
        raise ValidationError('Password must contain a number')

class UserSchema(Schema):
    password = fields.Str(
        required=True,
        validate=validate_password_strength
    )
```

### Nested Validation

**One-to-One:**
```python
class AddressSchema(Schema):
    street = fields.Str(required=True)
    city = fields.Str(required=True)
    zip_code = fields.Str(validate=Length(equal=5))

class UserSchema(Schema):
    username = fields.Str(required=True)
    address = fields.Nested(AddressSchema, required=True)

# Input:
{
    "username": "john",
    "address": {
        "street": "123 Main St",
        "city": "Boston",
        "zip_code": "02101"
    }
}
```

**One-to-Many:**
```python
class CommentSchema(Schema):
    text = fields.Str(required=True)
    author = fields.Str(required=True)

class PostSchema(Schema):
    title = fields.Str(required=True)
    comments = fields.List(fields.Nested(CommentSchema))

# Input:
{
    "title": "My Post",
    "comments": [
        {"text": "Great!", "author": "Alice"},
        {"text": "Thanks!", "author": "Bob"}
    ]
}
```

### File Upload Validation

```python
from werkzeug.utils import secure_filename
import magic  # python-magic for MIME detection

def validate_image(file):
    # Check file size (5MB limit)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > 5 * 1024 * 1024:
        raise ValidationError('File too large (max 5MB)')

    # Check file extension
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif']:
        raise ValidationError('Invalid file type')

    # Check MIME type (prevents fake extensions)
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    if mime not in ['image/jpeg', 'image/png', 'image/gif']:
        raise ValidationError('Invalid image format')

    # Check image dimensions
    from PIL import Image
    img = Image.open(file)
    if img.width > 2000 or img.height > 2000:
        raise ValidationError('Image too large (max 2000x2000)')
    file.seek(0)
```

### Cross-Field Validation

```python
class EventSchema(Schema):
    title = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data['end_date'] <= data['start_date']:
            raise ValidationError(
                'End date must be after start date',
                field_name='end_date'
            )
```

## 🛠️ Technologies Used

- **Marshmallow**: Schema validation library
- **python-magic**: MIME type detection
- **Pillow (PIL)**: Image validation
- **email-validator**: Advanced email checking
- **phonenumbers**: Phone number validation
- **bleach**: HTML sanitization

## 📝 Prerequisites

- Completed Chapter 4 (Authentication)
- Understanding of Python decorators
- Knowledge of regular expressions
- Familiarity with file handling

## 🚦 Ready Check

Before starting, you should be able to:
- [ ] Create Flask-RESTX endpoints with models
- [ ] Handle JSON request bodies
- [ ] Return error responses with status codes
- [ ] Work with Python decorators
- [ ] Understand try/except error handling

## 🔒 Validation Best Practices

### 1. Always validate on the server
```python
# ❌ Trusting client validation
# Client can bypass JavaScript validation!

# ✅ Always validate server-side
schema = UserSchema()
try:
    data = schema.load(request.json)
except ValidationError as err:
    return {'errors': err.messages}, 400
```

### 2. Provide clear error messages
```python
# ❌ Vague errors
raise ValidationError('Invalid input')

# ✅ Specific errors
raise ValidationError('Username must be 3-20 characters and contain only letters, numbers, and underscores')
```

### 3. Validate early, fail fast
```python
# ✅ Validate at the entry point
@posts_ns.route('/')
class PostList(Resource):
    def post(self):
        # Validate immediately
        schema = PostSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        # Now work with clean data
        post = Post(**data)
```

### 4. Sanitize untrusted input
```python
import bleach

def sanitize_html(text):
    # Allow only safe tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'a']
    allowed_attrs = {'a': ['href', 'title']}

    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
```

### 5. Use whitelists, not blacklists
```python
# ❌ Blacklist (can miss attacks)
if '<script>' in username or 'DROP TABLE' in username:
    raise ValidationError('Invalid characters')

# ✅ Whitelist (only allow safe characters)
if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
    raise ValidationError('Username must be 3-20 alphanumeric characters')
```

## 📊 Common Validation Patterns

### Email Validation
```python
from marshmallow import fields
from email_validator import validate_email, EmailNotValidError

class UserSchema(Schema):
    email = fields.Email(required=True)

    @validates('email')
    def validate_email_domain(self, value):
        try:
            # Deep validation (checks MX records)
            valid = validate_email(value, check_deliverability=True)
            normalized = valid.email
        except EmailNotValidError as e:
            raise ValidationError(str(e))

        # Block temporary email domains
        blocked_domains = ['tempmail.com', '10minutemail.com']
        domain = value.split('@')[1]
        if domain in blocked_domains:
            raise ValidationError('Temporary email addresses not allowed')
```

### Password Strength
```python
import re

def validate_password(password):
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

    # Check against common passwords
    common = ['password', '12345678', 'qwerty', 'abc123']
    if password.lower() in common:
        raise ValidationError('Password is too common')
```

### Phone Number
```python
import phonenumbers
from phonenumbers import NumberParseException

def validate_phone(phone_number, region='US'):
    try:
        parsed = phonenumbers.parse(phone_number, region)
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError('Invalid phone number')
    except NumberParseException:
        raise ValidationError('Invalid phone number format')
```

## 🚨 Common Mistakes to Avoid

### ❌ Not validating required fields
```python
# ❌ Assuming data exists
title = request.json['title']  # KeyError if missing!

# ✅ Using Marshmallow
class PostSchema(Schema):
    title = fields.Str(required=True)
```

### ❌ Validating output instead of input
```python
# ❌ Wrong direction
schema.dump(request.json)  # dump is for output!

# ✅ Correct
schema.load(request.json)  # load is for input validation
```

### ❌ Ignoring ValidationError
```python
# ❌ No error handling
data = schema.load(request.json)  # Crashes on invalid data!

# ✅ Proper error handling
try:
    data = schema.load(request.json)
except ValidationError as err:
    return {'errors': err.messages}, 400
```

### ❌ Not validating list length
```python
# ❌ No limit
tags = fields.List(fields.Str())  # User sends 10,000 tags!

# ✅ With limit
tags = fields.List(fields.Str(), validate=Length(max=10))
```

### ❌ Trusting file extensions
```python
# ❌ Only checking extension
if not filename.endswith('.jpg'):
    raise ValidationError('Invalid file')
# User renames virus.exe → virus.jpg!

# ✅ Check MIME type
import magic
mime = magic.from_buffer(file.read(1024), mime=True)
if mime not in ['image/jpeg', 'image/png']:
    raise ValidationError('Invalid image')
```

## 📚 Additional Resources

- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [OWASP Input Validation Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Python email-validator](https://github.com/JoshData/python-email-validator)
- [Bleach HTML Sanitization](https://bleach.readthedocs.io/)
- [Python Magic (MIME detection)](https://github.com/ahupp/python-magic)

## 🎯 Learning Outcomes

After completing this chapter, you will be able to:

✅ Implement comprehensive input validation with Marshmallow
✅ Create custom validators for business rules
✅ Validate nested and complex data structures
✅ Handle file upload validation securely
✅ Provide user-friendly error messages
✅ Sanitize untrusted user input
✅ Implement cross-field validation logic
✅ Build production-ready validation systems

## ⏭️ Next Chapter

[Chapter 6: Testing & Debugging](../06-testing/README.md) - Learn to write comprehensive tests, debug effectively, and ensure code quality.

---

**Security Note:** Never trust user input! Proper validation is your first line of defense against SQL injection, XSS, and data corruption. Validate everything!

**Ready to build bulletproof validation?** Start with the [demo project](demo/README.md)!
