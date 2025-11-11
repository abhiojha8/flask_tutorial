# Whiteboard Diagrams for Chapter 5: Data Validation

Visual explanations for teaching validation concepts during live coding sessions.

---

## DIAGRAM 1: Why Validation Matters

```
WITHOUT VALIDATION                    WITH VALIDATION
═══════════════════                  ═══════════════════

Client                               Client
  │                                   │
  │ {"age": -5}                      │ {"age": -5}
  │ {"email": "notvalid"}            │ {"email": "notvalid"}
  │ {"title": ""}                    │ {"title": ""}
  ↓                                   ↓
Server                               Server: VALIDATE
  │                                   │
  │ ❌ Saves garbage data!            │ ✅ Rejects invalid data
  ↓                                   │
Database                             │ Returns clear errors:
  ╔══════════════╗                    │ - "age must be >= 0"
  ║ age: -5      ║                    │ - "Invalid email"
  ║ email: "bad" ║                    │ - "Title required"
  ║ title: null  ║                    ↓
  ╚══════════════╝                   Client: Fix & retry!

  Security Issues:                   Benefits:
  - SQL Injection                    ✓ Data Integrity
  - XSS Attacks                      ✓ Security
  - Data Corruption                  ✓ User Experience
```

---

## DIAGRAM 2: Client-Side vs Server-Side Validation

```
CLIENT-SIDE VALIDATION              SERVER-SIDE VALIDATION
══════════════════════              ══════════════════════

Browser Form                        POST /users/register
┌──────────────────┐                ┌──────────────────┐
│ Username: admin  │                │                  │
│ [Submit]         │                │  Server receives │
└──────────────────┘                │  raw JSON:       │
     │                              │  {               │
     │ JavaScript checks:           │    "username":   │
     │ ✓ Not empty                  │    "admin"       │
     │ ✓ Min 3 chars                │  }               │
     │ ✓ Format OK                  │                  │
     │                              └──────────────────┘
     │ ❌ Can be bypassed!                  │
     │   - Disable JavaScript              │
     │   - Use curl/Postman                │ ✅ ALWAYS validates
     │   - Edit browser DOM                │
     ↓                                     ↓
Sends to server anyway              Marshmallow Schema
                                    ┌──────────────────┐
                                    │ @validates       │
                                    │ Check reserved   │
                                    │ Check duplicates │
                                    │ Check DB state   │
                                    └──────────────────┘

❌ Client-side only:                ✅ Server-side:
   Convenience, not security           True security
```

---

## DIAGRAM 3: Marshmallow Validation Flow

```
INPUT DATA                          MARSHMALLOW PROCESS
══════════════                     ═══════════════════════

{                                  1. LOAD (Deserialize & Validate)
  "username": "john",              ┌──────────────────────────┐
  "email": "john@example.com",     │ class UserSchema(Schema):│
  "age": 25,                       │   username = Str()       │
  "extra": "ignore"                │   email = Email()        │
}                                  │   age = Int()            │
       │                           └──────────────────────────┘
       │                                      │
       ↓                                      ↓
schema.load(data)                  2. FIELD VALIDATION
       │                           ┌──────────────────────────┐
       │                           │ ✓ Types match            │
       │                           │ ✓ Required fields present│
       │                           │ ✓ Built-in validators    │
       │                           │   Length, Range, Email   │
       │                           └──────────────────────────┘
       │                                      │
       │                                      ↓
       │                           3. CUSTOM VALIDATORS
       │                           ┌──────────────────────────┐
       │                           │ @validates('username')   │
       │                           │ def check_reserved():    │
       │                           │   if value in ['admin']: │
       │                           │     raise ValidationError│
       │                           └──────────────────────────┘
       │                                      │
       │                                      ↓
       │                           4. CROSS-FIELD VALIDATION
       │                           ┌──────────────────────────┐
       │                           │ @validates_schema        │
       │                           │ def check_dates():       │
       │                           │   if end < start:        │
       │                           │     raise ValidationError│
       │                           └──────────────────────────┘
       ↓                                      │
RESULT:                                       ↓
{                                  ✅ Clean, validated data
  "username": "john",              OR
  "email": "john@example.com",     ❌ ValidationError with details
  "age": 25
}
("extra" removed by EXCLUDE)
```

---

## DIAGRAM 4: Field-Level Validators

```
BUILT-IN VALIDATORS
═══════════════════

from marshmallow.validate import Length, Range, Email, OneOf

username = fields.Str(
    required=True,                  ┌─────────────────────┐
    validate=Length(min=3, max=50)  │ Length Validator    │
)                                   │                     │
         │                          │ Input: "ab"         │
         │                          │ Error: Too short!   │
         ↓                          │                     │
"ab" → ❌ Too short                 │ Input: "john"       │
"john" → ✅ Valid                   │ Success: ✓          │
                                    └─────────────────────┘

age = fields.Int(
    validate=Range(min=13, max=120) ┌─────────────────────┐
)                                   │ Range Validator     │
         │                          │                     │
         │                          │ Input: 10           │
         ↓                          │ Error: Too small!   │
10 → ❌ Too young                   │                     │
25 → ✅ Valid                       │ Input: 25           │
                                    │ Success: ✓          │
                                    └─────────────────────┘

role = fields.Str(
    validate=OneOf(['user', 'admin'])┌─────────────────────┐
)                                    │ OneOf Validator     │
         │                           │                     │
         │                           │ Input: "guest"      │
         ↓                           │ Error: Not in list! │
"guest" → ❌ Not allowed            │                     │
"admin" → ✅ Valid                  │ Input: "admin"      │
                                    │ Success: ✓          │
                                    └─────────────────────┘
```

---

## DIAGRAM 5: Custom Validators with @validates

```
DECORATOR-BASED CUSTOM VALIDATORS
══════════════════════════════════

class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

    @validates('username')
    def validate_username(self, value):
        ┌─────────────────────────────────┐
        │ VALIDATION LOGIC                │
        │                                 │
        │ 1. Check reserved names         │
        │    if value in ['admin']:       │
        │        raise ValidationError()  │
        │                                 │
        │ 2. Check database               │
        │    if User.query.filter(...):   │
        │        raise ValidationError()  │
        │                                 │
        │ 3. Custom business rules        │
        │    if not value[0].isalpha():   │
        │        raise ValidationError()  │
        └─────────────────────────────────┘

    @validates('password')
    def validate_password(self, value):
        ┌─────────────────────────────────┐
        │ PASSWORD STRENGTH CHECK         │
        │                                 │
        │ ✓ Length >= 8                   │
        │ ✓ Has uppercase                 │
        │ ✓ Has lowercase                 │
        │ ✓ Has digit                     │
        │ ✓ Has special char              │
        └─────────────────────────────────┘

EXECUTION FLOW:
══════════════

Input: {"username": "admin", "password": "weak"}
  │
  ↓
Field validation (types, required)
  │
  ↓
@validates('username') executes
  │
  ↓  ❌ "admin" is reserved!
  │
Return: {'username': ['Username is reserved']}
```

---

## DIAGRAM 6: Nested Schema Validation

```
NESTED OBJECT VALIDATION
════════════════════════

INPUT JSON:                         SCHEMAS:
═══════════                        ═════════

{                                  class AddressSchema(Schema):
  "username": "john",                  street = Str(required=True)
  "email": "john@ex.com",              city = Str(required=True)
  "address": {                         zip_code = Str()
    "street": "123 Main St",
    "city": "Boston",                  @validates('zip_code')
    "zip_code": "02101"                def check_format(self, value):
  }                                        if not re.match(r'^\d{5}$'):
}                                              raise ValidationError()

       │
       ↓                           class UserSchema(Schema):
schema.load(data)                      username = Str()
       │                               email = Email()
       │                               address = Nested(AddressSchema)
       ↓                                       │
                                               ↓
VALIDATION FLOW:                    ┌───────────────────────┐
                                    │ 1. Validate username  │
1. Validate top-level fields        │ 2. Validate email     │
   ✓ username OK                    └───────────────────────┘
   ✓ email OK                                  │
                                               ↓
2. Encounter "address" (Nested)     ┌───────────────────────┐
   ↓                                │ 3. Validate address:  │
   Pass to AddressSchema            │    ✓ street OK        │
   ┌─────────────────────┐          │    ✓ city OK          │
   │ Validate street     │          │    ✓ zip_code format  │
   │ Validate city       │          └───────────────────────┘
   │ Validate zip_code   │                     │
   │   @validates runs!  │                     ↓
   └─────────────────────┘          ✅ All fields valid!

ERROR STRUCTURE:
═══════════════

If nested validation fails:
{
  "errors": {
    "address": {
      "zip_code": ["Must be 5 digits"]
    }
  }
}
```

---

## DIAGRAM 7: List Validation with Nested Schemas

```
VALIDATING LISTS OF OBJECTS
════════════════════════════

INPUT:                              SCHEMA:
══════                             ════════

{                                  class CommentSchema(Schema):
  "title": "My Post",                  text = Str(required=True)
  "comments": [                        author = Str(required=True)
    {
      "text": "Great!",            class PostSchema(Schema):
      "author": "Alice"                title = Str()
    },                                 comments = List(
    {                                      Nested(CommentSchema)
      "text": "",                      )
      "author": "Bob"
    }
  ]
}

VALIDATION PROCESS:
═══════════════════

┌──────────────────────────────────────┐
│ schema.load(data)                    │
└──────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────┐
│ 1. Validate title                    │
│    ✓ "My Post" is valid              │
└──────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────┐
│ 2. Iterate over comments list        │
│                                      │
│    Comment 0:                        │
│    ┌────────────────────────┐        │
│    │ text: "Great!" ✓       │        │
│    │ author: "Alice" ✓      │        │
│    └────────────────────────┘        │
│                                      │
│    Comment 1:                        │
│    ┌────────────────────────┐        │
│    │ text: "" ❌ EMPTY!     │        │
│    │ author: "Bob" ✓        │        │
│    └────────────────────────┘        │
└──────────────────────────────────────┘
                │
                ↓
ERROR RESPONSE:
{
  "errors": {
    "comments": {
      "1": {                    ← Index of invalid item
        "text": ["Field may not be blank"]
      }
    }
  }
}
```

---

## DIAGRAM 8: Cross-Field Validation

```
@validates_schema DECORATOR
════════════════════════════

SCENARIO: Event Booking
═══════════════════════

Input:
{
  "title": "Conference",
  "start_date": "2025-01-15",
  "end_date": "2025-01-10"     ← PROBLEM: Before start!
}

class EventSchema(Schema):
    title = Str()
    start_date = DateTime()
    end_date = DateTime()

    @validates_schema
    def validate_dates(self, data, **kwargs):
        ┌──────────────────────────────────────┐
        │ Cross-Field Logic                    │
        │                                      │
        │ Access multiple fields:              │
        │   start = data['start_date']         │
        │   end = data['end_date']             │
        │                                      │
        │ Compare:                             │
        │   if end <= start:                   │
        │       raise ValidationError(         │
        │           'End must be after start', │
        │           field_name='end_date'      │
        │       )                              │
        └──────────────────────────────────────┘

EXECUTION:
══════════

1. Field validation
   ✓ title is string
   ✓ start_date is datetime
   ✓ end_date is datetime

2. @validates_schema runs
   ✓ Has access to ALL fields
   ✓ Can compare/cross-check
   ❌ end_date (Jan 10) before start_date (Jan 15)

3. Error returned
   {
     "errors": {
       "end_date": ["End must be after start"]
     }
   }

OTHER USE CASES:
════════════════
- Password confirmation match
- Discount price < regular price
- Minimum quantity based on product type
- Required field based on status
```

---

## DIAGRAM 9: File Upload Validation

```
FILE UPLOAD SECURITY
════════════════════

ATTACK SCENARIO:                    DEFENSE LAYERS:
════════════════                   ════════════════

virus.exe                          ┌─────────────────────────┐
    │                              │ 1. FILE SIZE            │
    │ Rename to:                   │    Max: 5MB             │
    ↓                              │    Prevents DoS         │
virus.jpg                          └─────────────────────────┘
    │                                        │
    │ Upload                                 ↓
    ↓                              ┌─────────────────────────┐
Server                             │ 2. EXTENSION CHECK      │
    │                              │    Allowed: .jpg, .png  │
    ❌ Trusts extension?           │    Block: .exe, .sh     │
    ↓                              └─────────────────────────┘
Executes virus!                              │
                                             ↓
                                   ┌─────────────────────────┐
PROPER VALIDATION:                 │ 3. MIME TYPE            │
══════════════════                 │    Use python-magic     │
                                   │    Verify actual type   │
def validate_upload(file):         │    .exe → "application" │
    ┌──────────────────┐           │    .jpg → "image/jpeg"  │
    │ 1. Check size    │           └─────────────────────────┘
    │    file.seek(0,  │                      │
    │      SEEK_END)   │                      ↓
    │    size=tell()   │           ┌─────────────────────────┐
    └──────────────────┘           │ 4. CONTENT VALIDATION   │
            │                      │    PIL Image.open()     │
            ↓                      │    Verify image valid   │
    ┌──────────────────┐           │    Check dimensions     │
    │ 2. Check ext     │           └─────────────────────────┘
    │    .rsplit('.')  │                      │
    │    if ext not in │                      ↓
    │      allowed     │           ┌─────────────────────────┐
    └──────────────────┘           │ 5. SECURE FILENAME      │
            │                      │    secure_filename()    │
            ↓                      │    Remove: ../, /, \    │
    ┌──────────────────┐           │    Prevent path         │
    │ 3. MIME check    │           │    traversal            │
    │    magic.from_   │           └─────────────────────────┘
    │      buffer()    │
    └──────────────────┘
            │
            ↓
    ┌──────────────────┐
    │ 4. PIL verify    │
    │    Image.open()  │
    │    Check dims    │
    └──────────────────┘
            │
            ↓
    ✅ Safe to save!
```

---

## DIAGRAM 10: Context-Aware Validation

```
PASSING CONTEXT TO SCHEMAS
═══════════════════════════

SCENARIO: User Quota Enforcement
═════════════════════════════════

Request: POST /posts
{
  "title": "My 6th Post Today"
}

Endpoint:
def post(self):
    user_id = get_current_user_id()  ← From JWT

    schema = PostSchema(
        context={'user_id': user_id}  ← Pass context!
    )

    data = schema.load(request.json)

Schema:
class PostSchema(Schema):
    title = Str()

    @validates_schema
    def check_quota(self, data, **kwargs):
        ┌────────────────────────────────────┐
        │ Access context:                    │
        │                                    │
        │ user_id = self.context['user_id'] │
        │                                    │
        │ Query database:                    │
        │ today = datetime.now().date()      │
        │ count = Post.query.filter(         │
        │     author_id=user_id,             │
        │     created_at >= today            │
        │ ).count()                          │
        │                                    │
        │ Enforce rule:                      │
        │ if count >= 5:                     │
        │     raise ValidationError(         │
        │         'Daily quota exceeded'     │
        │     )                              │
        └────────────────────────────────────┘

FLOW:
═════

User makes 1st-5th post → ✅ Allowed
User makes 6th post     → ❌ Quota exceeded!

OTHER CONTEXT USES:
═══════════════════
- Check user permissions/role
- Validate against user's existing data
- Enforce user-specific limits
- Conditional validation based on user state
```

---

## Usage During Live Coding

### When to Draw Each Diagram:

1. **Diagram 1** - Introduction: Why validation matters
2. **Diagram 2** - Before implementing first schema
3. **Diagram 3** - Explaining Marshmallow workflow
4. **Diagram 4** - When adding built-in validators
5. **Diagram 5** - Before creating @validates decorators
6. **Diagram 6** - When introducing nested schemas
7. **Diagram 7** - For list validation examples
8. **Diagram 8** - When implementing cross-field logic
9. **Diagram 9** - Before file upload exercise
10. **Diagram 10** - For quota/business rule validation

**Teaching Tip:** Draw these live, don't show finished diagrams! Students learn better when they see you build the concept step by step.
