# Simple Authentication App

A minimal Flask authentication demo focused on teaching core concepts.

## What's Different from the Full Demo?

### Simplified Structure

**Full Demo (`app.py`)** - 871 lines
- 3 models (User, Post, TokenBlacklist)
- Role-based access control (admin, author, reader)
- Posts with CRUD operations
- Admin endpoints
- Token refresh mechanism
- Logout with blacklisting
- Password change
- Profile updates

**Simple Demo (`simple_auth_app.py`)** - 309 lines
- 1 model (User only)
- 3 core endpoints (register, login, profile)
- Focus on authentication essentials
- No authorization complexity
- No token refresh/logout
- Pure learning example

## Core Concepts Taught

### 1. Password Security
```python
def set_password(self, password):
    """Hash password using bcrypt."""
    self.password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
```

**What you learn:**
- NEVER store passwords in plain text
- bcrypt automatically salts passwords
- One-way hashing (can't reverse)
- Verification without decryption

### 2. JWT Authentication
```python
# Login: Create token
access_token = create_access_token(identity=user.id)

# Protected route: Verify token
@jwt_required()
def get(self):
    user_id = get_jwt_identity()
```

**What you learn:**
- Stateless authentication (no session)
- Token contains user identity
- No database lookup for authentication
- Token in Authorization header

### 3. Protected Routes
```python
@auth_ns.route('/me')
class Profile(Resource):
    @jwt_required()  # This protects the endpoint
    def get(self):
        user_id = get_jwt_identity()  # Extract from token
```

**What you learn:**
- Decorator-based protection
- Automatic token validation
- Extract user from token
- No manual auth checking

## Quick Start

### 1. Install Dependencies
```bash
pip install flask flask-restx flask-sqlalchemy flask-jwt-extended flask-cors python-dotenv bcrypt
```

### 2. Set Environment Variables
Create `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/flask_tutorial
JWT_SECRET_KEY=your-secret-key-here
```

### 3. Run the App
```bash
python simple_auth_app.py
```

### 4. Test the Endpoints

**Register a User**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "password123"
  }'
```

**Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Get Profile (Protected)**
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Code Walkthrough

### Registration Flow
1. Client sends username, email, password
2. Server validates email format
3. Server validates password strength (8+ chars, letter + number)
4. Server checks for duplicate username/email
5. Server hashes password with bcrypt
6. Server creates user in database
7. Server returns user info (NOT password!)

### Login Flow
1. Client sends email, password
2. Server finds user by email
3. Server verifies password against hash
4. Server creates JWT token with user.id
5. Server returns token to client
6. Client stores token (localStorage/sessionStorage)

### Protected Route Flow
1. Client sends request with Authorization header
2. `@jwt_required()` decorator validates token
3. Decorator extracts user_id from token
4. Route handler uses `get_jwt_identity()` to get user_id
5. Route handler fetches user from database
6. Route handler returns user data

## Security Best Practices Demonstrated

### ✅ Password Hashing
- Uses bcrypt (industry standard)
- Automatic salting
- Slow by design (prevents brute force)

### ✅ Input Validation
- Email format validation
- Password strength requirements
- Duplicate checking

### ✅ Secure Password Storage
- NEVER store plain text
- NEVER return password_hash in API
- Use proper column type (VARCHAR 255)

### ✅ JWT Best Practices
- Short expiration (1 hour)
- Secret key from environment
- User ID as identity (not username)

## Common Mistakes Avoided

### ❌ Don't Do This
```python
# BAD: Storing plain password
user.password = data['password']

# BAD: Returning password
return {
    'username': user.username,
    'password': user.password  # NEVER!
}

# BAD: Weak password validation
if len(password) >= 6:  # Too short!
```

### ✅ Do This
```python
# GOOD: Hash password
user.set_password(data['password'])

# GOOD: Never return password
return {
    'username': user.username,
    'email': user.email
    # No password field!
}

# GOOD: Strong validation
if len(password) < 8 or not has_letter_and_number(password):
    return error
```

## Testing with Swagger

1. Open http://localhost:5000/docs
2. Try the `/api/auth/register` endpoint
3. Try the `/api/auth/login` endpoint
4. Copy the `access_token` from response
5. Click "Authorize" button at top
6. Enter: `Bearer <your_token>`
7. Try the `/api/auth/me` endpoint

## Next Steps

After understanding this simple version, study the full demo (`app.py`) to learn:
- Role-based authorization
- Token refresh mechanism
- Logout with token blacklisting
- Password change with verification
- Admin operations
- Resource ownership (posts)

## Comparison Table

| Feature | Simple Demo | Full Demo |
|---------|-------------|-----------|
| Models | 1 (User) | 3 (User, Post, TokenBlacklist) |
| Endpoints | 3 | 14 |
| Authentication | ✅ | ✅ |
| Authorization | ❌ | ✅ (Roles) |
| Token Refresh | ❌ | ✅ |
| Logout | ❌ | ✅ (Blacklist) |
| Password Change | ❌ | ✅ |
| Admin Panel | ❌ | ✅ |
| CRUD Operations | ❌ | ✅ (Posts) |
| Lines of Code | ~309 | ~871 |

## Key Takeaways

1. **Authentication** = Proving who you are (login)
2. **Authorization** = What you're allowed to do (roles/permissions)
3. **Hashing** = One-way transformation (can't reverse)
4. **JWT** = Stateless token containing user identity
5. **bcrypt** = Secure password hashing algorithm
6. **@jwt_required()** = Decorator to protect routes

This simple demo focuses on authentication essentials without the complexity of a full application, making it perfect for learning!
