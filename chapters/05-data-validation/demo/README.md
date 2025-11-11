# Chapter 5 Demo: Advanced Data Validation

This demo application showcases production-ready validation patterns using Marshmallow.

## Features

### 1. **Marshmallow Schema Validation**
- Field-level validation with built-in validators
- Type coercion and serialization
- Unknown field handling

### 2. **Custom Validators**
- Password strength validation
- Username blacklist checking
- Profanity filtering
- Phone number formatting

### 3. **Nested Validation**
- Nested schemas for complex objects
- List validation with nested items
- Hierarchical data validation (categories)

### 4. **Cross-Field Validation**
- Conditional requirements (publish_date when status=published)
- Date range validation
- Business rule enforcement

### 5. **Input Sanitization**
- SQL injection prevention
- XSS prevention
- Search query sanitization

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your DATABASE_URL from Chapter 3
# DATABASE_URL="postgresql://user:password@host:6543/postgres"
```

### 3. Run the Application

```bash
python app.py
```

### 4. Open Swagger UI

```
http://localhost:5000/swagger
```

## API Endpoints

### User Registration (`POST /users/register`)
**Validates:**
- Username: 3-50 chars, alphanumeric + underscore, starts with letter
- Email: Valid format, not temporary domain, unique
- Password: 8+ chars, uppercase, lowercase, number, special char
- Phone: Valid format (optional)
- Bio: Max 500 chars (optional)

**Try:**
```json
{
  "username": "admin",
  "email": "test@tempmail.com",
  "password": "weak"
}
```
Expected: Multiple validation errors!

### Create Post (`POST /posts`)
**Validates:**
- Title: 5-200 chars, no profanity, not all caps
- Content: 10+ chars, no profanity
- Tags: Max 10, unique, alphanumeric only
- Status: draft/published/archived
- Publish date: Required if published, not in past

**Try:**
```json
{
  "title": "My Post",
  "content": "Great content here",
  "tags": ["python", "flask", "python"],
  "status": "published"
}
```
Expected: Duplicate tag error + missing publish_date!

### Add Comment (`POST /posts/{id}/comments`)
**Validates:**
- Text: 1-1000 chars, no profanity, not too many caps
- Parent comment ID: Must exist and belong to same post

**Try:**
```json
{
  "text": "THIS IS SHOUTING!!!!!",
  "parent_comment_id": 999
}
```
Expected: Too many caps + invalid parent!

### Create Category (`POST /categories`)
**Validates:**
- Name: 2-50 chars, unique
- Parent ID: Must exist if provided

**Try:**
```json
{
  "name": "Technology",
  "parent_id": 999
}
```
Expected: Parent doesn't exist!

### Search (`POST /search`)
**Validates:**
- Query: 2-100 chars, sanitized for SQL injection
- Page: 1-1000
- Per page: 1-100
- No dangerous SQL characters

**Try:**
```json
{
  "query": "test'; DROP TABLE users; --",
  "page": 1,
  "per_page": 10
}
```
Expected: Sanitization error!

## Database Schema

```sql
-- Users with extended profile
CREATE TABLE users_validation (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    bio TEXT,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Posts with tags and status
CREATE TABLE posts_validation (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER REFERENCES users_validation(id),
    tags JSONB,  -- Array of tags
    category VARCHAR(50),
    status VARCHAR(20) DEFAULT 'draft',
    publish_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Comments with nested replies
CREATE TABLE comments_validation (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts_validation(id),
    user_id INTEGER REFERENCES users_validation(id),
    text TEXT NOT NULL,
    parent_comment_id INTEGER REFERENCES comments_validation(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Categories with hierarchy
CREATE TABLE categories_validation (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories_validation(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing Validation Scenarios

### 1. Password Validation
```bash
curl -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "weak"
  }'

# Expected errors:
# - Password must be at least 8 characters
# - Password must contain at least one uppercase letter
# - Password must contain at least one number
# - Password must contain at least one special character
```

### 2. Username Validation
```bash
curl -X POST http://localhost:5000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "test@example.com",
    "password": "ValidPass123!"
  }'

# Expected error:
# - Username "admin" is reserved
```

### 3. Cross-Field Validation
```bash
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Published Post",
    "content": "This is great content",
    "status": "published"
  }'

# Expected error:
# - publish_date is required when status is published
```

### 4. Nested Validation
```bash
curl -X POST http://localhost:5000/posts/1/comments \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Great post!",
    "parent_comment_id": 999
  }'

# Expected error:
# - Invalid parent comment
```

## Validation Error Response Format

All validation errors return 400 with this structure:

```json
{
  "errors": {
    "field_name": ["Error message 1", "Error message 2"],
    "another_field": ["Error message"]
  }
}
```

For nested fields:
```json
{
  "errors": {
    "address": {
      "zip_code": ["Length must be exactly 5"]
    }
  }
}
```

## Key Validation Patterns

### Field-Level Validators
```python
username = ma_fields.Str(
    required=True,
    validate=Length(min=3, max=50)
)
```

### Custom Validators
```python
@validates('username')
def validate_username(self, value):
    if value.lower() in ['admin', 'root']:
        raise ValidationError('Username is reserved')
```

### Cross-Field Validators
```python
@validates_schema
def validate_dates(self, data, **kwargs):
    if data['end_date'] < data['start_date']:
        raise ValidationError('End must be after start')
```

### Nested Schemas
```python
class PostSchema(Schema):
    author = ma_fields.Nested(UserSchema)
    comments = ma_fields.List(ma_fields.Nested(CommentSchema))
```

## Common Validation Mistakes

### ❌ Not handling ValidationError
```python
data = schema.load(request.json)  # Will crash!
```

### ✅ Proper error handling
```python
try:
    data = schema.load(request.json)
except ValidationError as err:
    return {'errors': err.messages}, 400
```

### ❌ Using dump instead of load
```python
data = schema.dump(request.json)  # Wrong direction!
```

### ✅ Correct usage
```python
data = schema.load(request.json)  # load = deserialize & validate
```

## Security Considerations

1. **Always validate on server** - Never trust client-side validation
2. **Sanitize all input** - Prevent SQL injection, XSS
3. **Use whitelists** - Define what's allowed, not what's forbidden
4. **Validate file uploads** - Check size, MIME type, content
5. **Limit input length** - Prevent DoS attacks
6. **Provide clear errors** - Help users fix issues without exposing system details

## Resources

- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [Validation Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Flask-RESTX](https://flask-restx.readthedocs.io/)

## Next Steps

After exploring the demo:
1. Complete the 5 exercises in `../exercises/`
2. Study the whiteboard diagrams
3. Follow the live coding guide
4. Implement validation in your own projects

---

**Remember:** Good validation is your first line of defense against bad data and security vulnerabilities!
