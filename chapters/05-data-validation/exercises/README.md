# Chapter 5 Exercises: Data Validation & Error Handling

These exercises build your understanding of Marshmallow schemas, custom validators, nested validation, and file upload security.

## Prerequisites

- Completed Chapter 4 (Authentication)
- Understanding of Python decorators
- Basic knowledge of regular expressions
- Familiarity with file handling

## Setup for All Exercises

Each exercise has its own directory with:
- `app.py` - Starter code with TODOs
- `README.md` - Exercise instructions
- `.env.example` - Environment template

**Copy your database credentials:**
```bash
# Use the same DATABASE_URL from Chapter 4
cp ../../04-authentication/demo/.env .env
# Add any additional secrets if needed
```

---

## Exercise 1: Basic Marshmallow Schemas 🟢

**File:** `exercise_1_basic_schemas/app.py`

**Learning Objectives:**
- Define Marshmallow schemas with typed fields
- Use built-in validators (Length, Range, Email)
- Handle validation errors gracefully
- Return user-friendly error messages

**What You'll Build:**
- User registration endpoint with validation
- Post creation endpoint with validation
- Field-level validators
- Error response formatting

**Key Concepts:**
- Schema vs Model (validation vs database)
- fields.Str, fields.Int, fields.Email
- required=True parameter
- ValidationError handling

**Success Criteria:**
- ✅ Invalid email format returns 400 with error
- ✅ Missing required fields returns 400
- ✅ Username too short/long returns 400
- ✅ Valid data creates resource and returns 201

---

## Exercise 2: Custom Validators 🟢

**File:** `exercise_2_custom_validators/app.py`

**Learning Objectives:**
- Create custom validation functions
- Use @validates decorator for methods
- Implement password strength checking
- Build reusable validators

**What You'll Build:**
- Password strength validator (8+ chars, uppercase, number, special char)
- Username blacklist validator (no 'admin', 'root', etc.)
- Custom email domain validator (block temporary emails)
- Phone number format validator

**Key Concepts:**
- @validates('field_name') decorator
- ValidationError raising
- Regular expressions for patterns
- Reusable validation functions

**Success Criteria:**
- ✅ Weak password returns specific error message
- ✅ Reserved username returns 400
- ✅ Temporary email domain blocked
- ✅ Invalid phone format returns 400

---

## Exercise 3: Nested Validation 🟡

**File:** `exercise_3_nested_validation/app.py`

**Learning Objectives:**
- Define nested schemas
- Validate one-to-one relationships
- Validate one-to-many relationships (lists)
- Handle complex object validation

**What You'll Build:**
- User schema with nested address
- Post schema with nested author info
- Comment schema with nested user data
- List validation for tags and categories

**Key Concepts:**
- fields.Nested() for relationships
- fields.List(fields.Nested()) for arrays
- many=True for list serialization
- Recursive validation

**Success Criteria:**
- ✅ Invalid nested address returns field-specific error
- ✅ List of comments validates each item
- ✅ Empty required nested object returns 400
- ✅ Valid nested data creates related objects

---

## Exercise 4: File Upload Validation 🟡

**File:** `exercise_4_file_upload/app.py`

**Learning Objectives:**
- Validate file size limits
- Check file extensions and MIME types
- Verify image dimensions with PIL
- Secure filename handling
- Detect potentially malicious files

**What You'll Build:**
- Image upload endpoint for posts
- File size validation (max 5MB)
- Extension whitelist (.jpg, .png, .gif)
- MIME type verification
- Image dimension checking (max 2000x2000)

**Key Concepts:**
- werkzeug.utils.secure_filename()
- python-magic for MIME detection
- PIL/Pillow for image validation
- File size checking
- Security considerations

**Success Criteria:**
- ✅ File > 5MB returns 400
- ✅ .exe file disguised as .jpg blocked
- ✅ Image > 2000x2000 returns 400
- ✅ Valid image uploads successfully
- ✅ Filename is sanitized (secure_filename)

---

## Exercise 5: Complex Business Rules 🔴

**File:** `exercise_5_business_rules/app.py`

**Learning Objectives:**
- Implement cross-field validation
- Use @validates_schema for multi-field checks
- Build context-aware validators
- Implement quota and rate limiting validation
- Create conditional required fields

**What You'll Build:**
- Event schema (end_date must be after start_date)
- Post creation with user quota (max 5 posts/day)
- Unique tag validation across user's posts
- Conditional validation (if published=true, content required)
- Price range validation (discount_price < regular_price)

**Key Concepts:**
- @validates_schema decorator
- Cross-field validation
- Database queries in validators
- Context passing to schemas
- Conditional logic in validation

**Success Criteria:**
- ✅ End date before start date returns 400
- ✅ 6th post in one day blocked with quota error
- ✅ Duplicate tag returns 409
- ✅ Publishing without content returns 400
- ✅ Discount > regular price returns 400

---

## Testing Your Solutions

### Using Swagger UI

1. Run your exercise:
   ```bash
   cd exercise_X_name
   python app.py
   ```

2. Open http://localhost:5000/swagger

3. Test validation scenarios:
   - Try invalid data → See error messages
   - Try valid data → Success
   - Check error response format

### Using curl

```bash
# Test basic validation
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"ab","email":"invalid"}'
# Should return 400 with validation errors

# Test custom validators
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"test@tempmail.com","password":"weak"}'
# Should return 400 with specific errors

# Test nested validation
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Post",
    "author": {"name": "", "email": "invalid"},
    "comments": [{"text": ""}]
  }'
# Should return 400 with nested field errors

# Test file upload
curl -X POST http://localhost:5000/posts/1/image \
  -F "file=@large_image.jpg"
# Should validate file size/type

# Test business rules
curl -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{"title":"Event","start_date":"2025-01-15","end_date":"2025-01-10"}'
# Should return 400 - end before start
```

### Using Python requests

```python
import requests

# Test validation errors
response = requests.post('http://localhost:5000/users', json={
    'username': 'ab',  # Too short
    'email': 'invalid',  # Invalid format
    'password': 'weak'  # Too weak
})

print(response.status_code)  # 400
print(response.json())  # {'errors': {...}}
```

---

## Common Issues & Solutions

### "ValidationError not caught"
- Make sure you're using try/except around schema.load()
- Check that you're returning the error in the correct format

### "Field required" for optional fields
- Don't use `required=True` for optional fields
- Use `missing=None` or provide a default value

### "Nested validation not working"
- Verify you're using `fields.Nested(SchemaClass)`
- For lists: `fields.List(fields.Nested(SchemaClass))`

### "File validation fails for valid files"
- Install python-magic: `pip install python-magic`
- On Windows, may need python-magic-bin
- Check file.seek(0) after reading file

### "Custom validator not called"
- Verify decorator: `@validates('exact_field_name')`
- Check field name matches schema field exactly

---

## Error Response Format

All exercises should return errors in this format:

```json
{
  "errors": {
    "username": ["Username must be 3-20 characters"],
    "email": ["Not a valid email address"],
    "password": ["Password must contain uppercase letter"]
  }
}
```

For nested fields:
```json
{
  "errors": {
    "address": {
      "zip_code": ["Length must be exactly 5"]
    },
    "comments": {
      "0": {
        "text": ["Field may not be blank"]
      }
    }
  }
}
```

---

## Learning Path

```
Exercise 1 (Basic Schemas)
    ↓
Exercise 2 (Custom Validators)
    ↓
Exercise 3 (Nested Validation)
    ↓
Exercise 4 (File Upload)
    ↓
Exercise 5 (Business Rules)
```

Complete them in order! Each builds on the previous one.

---

## Validation Patterns Cheat Sheet

### Required Field
```python
username = fields.Str(required=True)
```

### Length Validation
```python
from marshmallow.validate import Length
username = fields.Str(validate=Length(min=3, max=20))
```

### Range Validation
```python
from marshmallow.validate import Range
age = fields.Int(validate=Range(min=13, max=120))
```

### Email Validation
```python
email = fields.Email(required=True)
```

### Enum Validation
```python
from marshmallow.validate import OneOf
role = fields.Str(validate=OneOf(['user', 'admin', 'moderator']))
```

### Custom Validator
```python
@validates('username')
def validate_username(self, value):
    if value.lower() in ['admin', 'root']:
        raise ValidationError('Username is reserved')
```

### Nested Schema
```python
class AddressSchema(Schema):
    street = fields.Str(required=True)

class UserSchema(Schema):
    address = fields.Nested(AddressSchema)
```

### List of Objects
```python
comments = fields.List(fields.Nested(CommentSchema))
```

### Cross-Field Validation
```python
@validates_schema
def validate_dates(self, data, **kwargs):
    if data['end_date'] < data['start_date']:
        raise ValidationError('End must be after start')
```

---

## Solutions

Solutions are available in the `solutions` branch:

```bash
git checkout solutions
cd chapters/05-data-validation/exercises/exercise_X_name/
```

But try solving them yourself first! Debugging validation errors is a critical skill.

---

## Resources

- [Marshmallow Docs](https://marshmallow.readthedocs.io/) - Official documentation
- [Marshmallow Quickstart](https://marshmallow.readthedocs.io/en/stable/quickstart.html) - Getting started
- [Field Validators](https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html) - Built-in validators
- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) - Security guide

---

## Tips for Success

1. **Read error messages carefully** - Marshmallow gives detailed feedback
2. **Test edge cases** - Try empty strings, None, very long values
3. **Use Swagger UI** - Visual testing is faster than curl
4. **Start simple** - Get basic validation working, then add complexity
5. **Print debug info** - Use `print(request.json)` to see what you're receiving

---

Happy validating! 🛡️
