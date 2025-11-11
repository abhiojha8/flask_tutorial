# Chapter 4 Exercises: Authentication & Authorization

These exercises build your understanding of JWT authentication, password security, and role-based access control.

## Prerequisites

- Completed Chapter 3 (Database Integration)
- Understanding of HTTP headers
- Basic security awareness

## Setup for All Exercises

Each exercise has its own directory with:
- `app.py` - Starter code with TODOs
- `README.md` - Exercise instructions
- `.env.example` - Environment template

**Copy your database credentials:**
```bash
# Use the same DATABASE_URL from Chapter 3
cp ../../03-database-integration/demo/.env .env
# Add JWT_SECRET_KEY
echo 'JWT_SECRET_KEY=your-generated-secret' >> .env
```

**Generate JWT secret:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Exercise 1: User Registration & Password Hashing 🟢

**File:** `exercise_1_registration/app.py`

**Learning Objectives:**
- Implement secure password hashing with bcrypt
- Validate email format with regex
- Check for duplicate users
- Return appropriate HTTP status codes

**What You'll Build:**
- POST /auth/register endpoint
- User model with password hashing methods
- Email and password validation
- Duplicate checking

**Key Concepts:**
- Why NEVER store plain-text passwords
- How bcrypt automatically salts passwords
- Email validation with regex
- 409 Conflict vs 400 Bad Request

**Success Criteria:**
- ✅ Passwords are hashed before storage
- ✅ Invalid emails return 400
- ✅ Duplicate usernames/emails return 409
- ✅ Successful registration returns 201

---

## Exercise 2: Login & JWT Token Generation 🟢

**File:** `exercise_2_login/app.py`

**Learning Objectives:**
- Verify passwords against hashes
- Generate JWT access and refresh tokens
- Set appropriate token expiration
- Handle invalid credentials

**What You'll Build:**
- POST /auth/login endpoint
- Password verification logic
- JWT token generation
- Token response structure

**Key Concepts:**
- Access tokens (short-lived)
- Refresh tokens (long-lived)
- JWT payload structure
- Secure credential verification

**Success Criteria:**
- ✅ Correct credentials return tokens
- ✅ Wrong password returns 401
- ✅ Tokens include user_id in payload
- ✅ Access token expires in 1 hour

---

## Exercise 3: Protected Routes with JWT 🟡

**File:** `exercise_3_protected_routes/app.py`

**Learning Objectives:**
- Use @jwt_required decorator
- Extract user from JWT token
- Implement GET /auth/me endpoint
- Handle missing/invalid tokens

**What You'll Build:**
- Protected endpoint requiring authentication
- User profile retrieval from token
- Token validation and error handling
- Update profile functionality

**Key Concepts:**
- Bearer token authentication
- Extracting identity from JWT
- Token expiration handling
- Authorization header format

**Success Criteria:**
- ✅ Request without token returns 401
- ✅ Request with valid token succeeds
- ✅ Expired token returns 401
- ✅ User can view and update profile

---

## Exercise 4: Role-Based Access Control 🟡

**File:** `exercise_4_rbac/app.py`

**Learning Objectives:**
- Implement role-based permissions
- Create custom @require_role decorator
- Restrict endpoints by role
- Understand authorization vs authentication

**What You'll Build:**
- User roles (reader, author, admin)
- Custom decorator for role checking
- Role-restricted endpoints
- Permission matrix

**Key Concepts:**
- Authentication: Who are you?
- Authorization: What can you do?
- Role-based access control (RBAC)
- Decorator pattern in Python

**Success Criteria:**
- ✅ Readers cannot create posts
- ✅ Authors can create posts
- ✅ Admins can delete any post
- ✅ Users get 403 for unauthorized actions

---

## Exercise 5: Token Refresh & Logout 🔴

**File:** `exercise_5_refresh_tokens/app.py`

**Learning Objectives:**
- Implement token refresh mechanism
- Create token blacklist for logout
- Handle token expiration gracefully
- Understand token lifecycle

**What You'll Build:**
- POST /auth/refresh endpoint
- POST /auth/logout endpoint
- Token blacklist table
- Token revocation callback

**Key Concepts:**
- Why short-lived access tokens
- Refresh tokens for convenience
- Token blacklisting (logout)
- JWT callbacks

**Success Criteria:**
- ✅ Expired access token can be refreshed
- ✅ Logout blacklists current token
- ✅ Blacklisted token returns 401
- ✅ Refresh token lasts 30 days

---

## Testing Your Solutions

### Using Swagger UI

1. Run your exercise:
   ```bash
   cd exercise_X_name
   python app.py
   ```

2. Open http://localhost:5000/swagger

3. Test the flow:
   - Register a user
   - Login to get token
   - Click "Authorize" and enter: `Bearer <your_token>`
   - Test protected endpoints

### Using curl

```bash
# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123"}'

# Save the token, then:
TOKEN="your-token-here"

# Protected endpoint
curl http://localhost:5000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Common Issues & Solutions

### "Token has expired"
- Tokens expire after 1 hour
- Use refresh token to get new access token
- Or login again

### "Missing Authorization Header"
- Make sure to include: `Authorization: Bearer <token>`
- In Swagger, use the "Authorize" button

### "Signature verification failed"
- JWT_SECRET_KEY changed
- Token was modified
- Get a new token by logging in

### "User not found" after login
- Token contains wrong user_id
- User was deleted from database
- Check token payload on jwt.io

---

## Learning Path

```
Exercise 1 (Registration)
    ↓
Exercise 2 (Login)
    ↓
Exercise 3 (Protected Routes)
    ↓
Exercise 4 (RBAC)
    ↓
Exercise 5 (Refresh & Logout)
```

Complete them in order! Each builds on the previous one.

---

## Solutions

Solutions are available in the `solutions` branch:

```bash
git checkout solutions
cd chapters/04-authentication/exercises/exercise_X_name/
```

But try solving them yourself first! The struggle is where learning happens.

---

## Resources

- [JWT.io](https://jwt.io/) - Decode and verify JWTs
- [bcrypt docs](https://pypi.org/project/bcrypt/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [OWASP Auth Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

Happy coding! 🚀
