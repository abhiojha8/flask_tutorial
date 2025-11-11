# Chapter 4: Authentication & Authorization with JWT

## 🎯 Chapter Goals

By the end of this chapter, you will:
- Understand authentication vs authorization
- Implement secure user registration and login
- Use JWT (JSON Web Tokens) for stateless authentication
- Hash passwords securely with bcrypt
- Protect API endpoints with authentication decorators
- Implement role-based access control (RBAC)
- Handle token refresh and expiration
- Build a complete authentication system

## 📚 What You'll Learn

### Part 1: Authentication Fundamentals
- What is authentication? (Who are you?)
- What is authorization? (What can you do?)
- Sessions vs Tokens explained
- Why JWT for modern APIs?
- Security best practices

### Part 2: Password Security
- Why you NEVER store passwords in plain text
- Password hashing with bcrypt
- Salt and pepper concepts
- Password strength validation
- Secure password reset flows

### Part 3: JWT Deep Dive
- What is a JWT token?
- Token structure (header.payload.signature)
- Creating and verifying tokens
- Token expiration and refresh
- Where to store tokens (client-side)

### Part 4: Practical Implementation
- User registration endpoint
- Login endpoint (return JWT)
- Protected routes with decorators
- Token refresh mechanism
- Role-based permissions
- Logout and token blacklisting

## 🚀 Demo Project: Secure Blog Platform API

We'll add authentication to our blog platform:

**Features:**
- User registration with email validation
- Secure login with JWT tokens
- Password hashing with bcrypt
- Protected endpoints (create/update/delete posts)
- Public endpoints (read posts)
- Role-based access (admin, author, reader)
- Token refresh mechanism
- User profile management

**API Endpoints:**
```
Public:
  POST   /auth/register        - Create account
  POST   /auth/login           - Get JWT token
  GET    /posts                - List all posts (public)
  GET    /posts/{id}           - View post (public)

Protected (requires token):
  GET    /auth/me              - Get current user profile
  PUT    /auth/me              - Update profile
  POST   /auth/refresh         - Refresh JWT token
  POST   /posts                - Create post (author)
  PUT    /posts/{id}           - Update own post (author)
  DELETE /posts/{id}           - Delete own post (author/admin)

Admin only:
  GET    /admin/users          - List all users
  DELETE /admin/users/{id}     - Delete user
```

## 💻 Exercises

### Exercise 1: User Registration & Password Hashing 🟢
**Topics:** Password hashing, email validation, duplicate checking
- Implement user registration endpoint
- Hash passwords with bcrypt
- Validate email format and uniqueness
- Return appropriate error messages

### Exercise 2: Login & JWT Generation 🟢
**Topics:** Authentication, JWT creation, token structure
- Implement login endpoint
- Verify password against hash
- Generate JWT token with user claims
- Return token with expiration time

### Exercise 3: Protected Routes 🟡
**Topics:** Decorators, token validation, middleware
- Create `@require_auth` decorator
- Extract and validate JWT from headers
- Decode token and get user info
- Protect specific endpoints

### Exercise 4: Role-Based Access Control 🟡
**Topics:** Authorization, permissions, roles
- Add roles to user model (admin, author, reader)
- Create `@require_role` decorator
- Implement permission checking
- Build admin-only endpoints

### Exercise 5: Token Refresh & Advanced Security 🔴
**Topics:** Token refresh, blacklisting, security
- Implement refresh token mechanism
- Add token blacklist (logout)
- Handle expired tokens gracefully
- Implement password change flow

## 🎓 Learning Path

```
1. Read: Authentication concepts (theory)
   ↓
2. Demo: See JWT auth in action
   ↓
3. Exercise 1: Registration & hashing
   ↓
4. Exercise 2: Login & tokens
   ↓
5. Exercise 3: Protected routes
   ↓
6. Exercise 4: Role-based access
   ↓
7. Exercise 5: Advanced security
```

## 📖 Key Concepts

### What is Authentication?
**Authentication** = Verifying identity ("Who are you?")

Think of it like showing your ID at airport security:
1. You claim to be "John Doe" (username)
2. You prove it with your passport (password)
3. Security verifies and lets you through (JWT token)

### What is Authorization?
**Authorization** = Checking permissions ("What can you do?")

After you're in the airport (authenticated):
- Business class ticket → Access to lounge (authorized)
- Economy ticket → No lounge access (not authorized)

### Sessions vs Tokens

**Sessions (traditional web apps):**
```
User logs in → Server stores session in memory/DB
            → Server sends session ID cookie
            → Every request sends cookie
            → Server looks up session
```
❌ Doesn't scale (need shared session store)
❌ Server must track all sessions
❌ Doesn't work well for mobile apps

**JWT Tokens (modern APIs):**
```
User logs in → Server creates JWT token (signed)
            → Returns token to client
            → Client stores token (localStorage)
            → Client sends token in header
            → Server verifies signature (no DB lookup!)
```
✅ Stateless (no server-side storage)
✅ Scales horizontally
✅ Works great for mobile/SPA
✅ Can include user data in token

### JWT Structure

A JWT has three parts separated by dots:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsImV4cCI6MTYxNjI0MDIyMn0.5mhBHqs5_DTLdINd9p5m7ZJ6XD0Xc55kIaCRY5r6HRA
  └── Header ──┘  └────── Payload (claims) ────┘ └─── Signature ───┘
```

**Header:** Algorithm used (HS256, RS256)
**Payload:** User data (user_id, roles, expiration)
**Signature:** Proves token hasn't been tampered with

### Password Security

**❌ NEVER do this:**
```python
user.password = password  # Plain text! Anyone with DB access can see it!
```

**✅ ALWAYS do this:**
```python
from bcrypt import hashpw, gensalt, checkpw

# Storing password
hashed = hashpw(password.encode('utf-8'), gensalt())
user.password_hash = hashed

# Verifying password
if checkpw(password.encode('utf-8'), user.password_hash):
    # Password correct!
```

**Why bcrypt?**
- Automatically salted (no two hashes are the same)
- Slow by design (prevents brute force attacks)
- Future-proof (can increase work factor)

## 🛠️ Technologies Used

- **Flask-JWT-Extended**: JWT token management
- **bcrypt**: Password hashing
- **python-dotenv**: Secret key management
- **SQLAlchemy**: User model storage
- **Flask-RESTX**: API documentation

## 📝 Prerequisites

- Completed Chapter 3 (Database Integration)
- Understanding of HTTP headers
- Basic security awareness

## 🚦 Ready Check

Before starting, you should be able to:
- [ ] Create database models with SQLAlchemy
- [ ] Handle POST requests with JSON bodies
- [ ] Return different HTTP status codes
- [ ] Query database with filters
- [ ] Understand what environment variables are

## 🔒 Security Best Practices

### 1. Never hardcode secrets
```python
# ❌ Bad
SECRET_KEY = "mysecretkey123"

# ✅ Good
SECRET_KEY = os.getenv('SECRET_KEY')
```

### 2. Use HTTPS in production
```python
# JWTs can be intercepted on HTTP!
# Always use HTTPS to encrypt the connection
```

### 3. Set reasonable token expiration
```python
# ✅ Good
access_token_expires = timedelta(hours=1)  # Short-lived
refresh_token_expires = timedelta(days=30)  # Longer-lived
```

### 4. Validate all inputs
```python
# Email format, password strength, etc.
if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
    return {'error': 'Invalid email format'}, 400
```

### 5. Rate limit auth endpoints
```python
# Prevent brute force attacks
# Max 5 login attempts per minute per IP
```

## 📊 Common Authentication Flows

### Registration Flow
```
Client                          Server
  │                               │
  │ POST /auth/register          │
  │ { email, password }          │
  ├──────────────────────────────>│
  │                               │ 1. Validate email format
  │                               │ 2. Check if email exists
  │                               │ 3. Hash password with bcrypt
  │                               │ 4. Save user to database
  │                               │
  │ 201 Created                   │
  │ { id, email, created_at }    │
  │<──────────────────────────────┤
```

### Login Flow
```
Client                          Server
  │                               │
  │ POST /auth/login             │
  │ { email, password }          │
  ├──────────────────────────────>│
  │                               │ 1. Find user by email
  │                               │ 2. Verify password hash
  │                               │ 3. Generate JWT token
  │                               │
  │ 200 OK                        │
  │ { access_token, expires }    │
  │<──────────────────────────────┤
  │                               │
  │ Store token in localStorage   │
  │                               │
```

### Protected Endpoint Flow
```
Client                          Server
  │                               │
  │ GET /posts                   │
  │ Authorization: Bearer <jwt>  │
  ├──────────────────────────────>│
  │                               │ 1. Extract token from header
  │                               │ 2. Verify signature
  │                               │ 3. Check expiration
  │                               │ 4. Decode user_id
  │                               │ 5. Process request
  │                               │
  │ 200 OK                        │
  │ { posts: [...] }             │
  │<──────────────────────────────┤
```

## 🚨 Common Mistakes to Avoid

### ❌ Storing tokens in cookies (for SPA/mobile)
Use localStorage or secure cookie with httpOnly flag

### ❌ Putting sensitive data in JWT payload
The payload is BASE64-encoded, not encrypted! Anyone can decode it.
```python
# ❌ Bad
token = create_token({'user_id': 1, 'password': 'secret123'})

# ✅ Good
token = create_token({'user_id': 1, 'role': 'admin'})
```

### ❌ Not handling expired tokens
```python
# ✅ Always catch JWT exceptions
try:
    decode_token(token)
except ExpiredSignatureError:
    return {'error': 'Token expired'}, 401
```

### ❌ Using the same secret for dev and production
Each environment should have its own secret key!

### ❌ No password strength requirements
```python
# ✅ Enforce minimum standards
if len(password) < 8:
    return {'error': 'Password must be at least 8 characters'}, 400
```

## 📚 Additional Resources

- [JWT.io](https://jwt.io/) - Decode and verify JWTs
- [OWASP Authentication Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Flask-JWT-Extended Docs](https://flask-jwt-extended.readthedocs.io/)
- [bcrypt explained](https://auth0.com/blog/hashing-in-action-understanding-bcrypt/)

## 🎯 Learning Outcomes

After completing this chapter, you will be able to:

✅ Implement secure user registration with password hashing
✅ Create login endpoints that return JWT tokens
✅ Protect API endpoints with authentication
✅ Implement role-based access control
✅ Handle token expiration and refresh
✅ Follow authentication security best practices
✅ Debug authentication issues effectively

## ⏭️ Next Chapter

[Chapter 5: Data Validation & Error Handling](../05-data-validation/README.md) - Learn advanced input validation, custom validators, and comprehensive error handling patterns.

---

**Security Note:** Authentication is critical for production applications. Take time to understand each concept thoroughly. A single security mistake can compromise your entire application!

**Ready to secure your API?** Start with the [demo project](demo/README.md)!
