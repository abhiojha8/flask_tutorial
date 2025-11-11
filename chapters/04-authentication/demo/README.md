# Demo: Secure Blog Platform with JWT Authentication

This demo showcases a complete authentication system built with Flask, demonstrating industry-standard security practices.

## Features

✅ **User Registration**
- Email validation
- Password strength requirements
- bcrypt password hashing
- Duplicate checking

✅ **User Login**
- JWT token generation
- Access tokens (1 hour)
- Refresh tokens (30 days)
- Secure password verification

✅ **Protected Routes**
- JWT token validation
- Role-based access control (RBAC)
- Custom decorators (`@require_role`)
- Token blacklisting for logout

✅ **User Management**
- Profile viewing and editing
- Secure password changes
- Account activation/deactivation

✅ **Blog Posts**
- Create posts (author/admin only)
- Public reading of published posts
- Authors edit own posts
- Admins edit any post

✅ **Admin Operations**
- View all users
- Delete users
- Toggle account status

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required values:
- `DATABASE_URL`: Your PostgreSQL connection string (from Supabase)
- `JWT_SECRET_KEY`: A secure random string (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)

### 3. Run the Application

```bash
python app.py
```

The app will start on http://localhost:5000

### 4. Access Swagger UI

Open http://localhost:5000/swagger in your browser

## Quick Start Guide

### 1. Register a User

**POST** `/auth/register`

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role": "author"
}
```

Roles: `reader`, `author`, `admin`

### 2. Login

**POST** `/auth/login`

```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Copy the `access_token` for the next steps.

### 3. Use the Token

In Swagger UI:
1. Click the **"Authorize"** button (top right)
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize"

Or in curl/Postman:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:5000/auth/me
```

### 4. Create a Post (requires author role)

**POST** `/posts`

```json
{
  "title": "My First Blog Post",
  "content": "This is the content of my first post...",
  "is_published": true
}
```

### 5. View Your Profile

**GET** `/auth/me`

Returns your user information.

## Authentication Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. POST /auth/register
       │    { username, email, password }
       │
       v
┌─────────────┐
│   Server    │  ─→ Hash password with bcrypt
│             │  ─→ Store in database
└──────┬──────┘
       │
       │ 2. POST /auth/login
       │    { email, password }
       │
       v
┌─────────────┐
│   Server    │  ─→ Verify password
│             │  ─→ Generate JWT token
└──────┬──────┘
       │
       │ 3. Returns JWT token
       │
       v
┌─────────────┐
│   Client    │  ─→ Store token
│             │  ─→ Include in future requests
└──────┬──────┘
       │
       │ 4. GET /posts
       │    Authorization: Bearer <token>
       │
       v
┌─────────────┐
│   Server    │  ─→ Verify token signature
│             │  ─→ Decode user_id from token
│             │  ─→ Check permissions
│             │  ─→ Process request
└─────────────┘
```

## Role-Based Access Control

| Endpoint | Reader | Author | Admin |
|----------|--------|--------|-------|
| POST /auth/register | ✅ | ✅ | ✅ |
| POST /auth/login | ✅ | ✅ | ✅ |
| GET /auth/me | ✅ | ✅ | ✅ |
| PUT /auth/me | ✅ | ✅ | ✅ |
| GET /posts (published) | ✅ | ✅ | ✅ |
| POST /posts | ❌ | ✅ | ✅ |
| PUT /posts/:id (own) | ❌ | ✅ | ✅ |
| PUT /posts/:id (any) | ❌ | ❌ | ✅ |
| DELETE /posts/:id (own) | ❌ | ✅ | ✅ |
| DELETE /posts/:id (any) | ❌ | ❌ | ✅ |
| GET /admin/users | ❌ | ❌ | ✅ |
| DELETE /admin/users/:id | ❌ | ❌ | ✅ |

## Security Features

### Password Security
- **bcrypt hashing**: Industry-standard password hashing
- **Automatic salting**: Each password gets a unique salt
- **Strength validation**: Min 8 chars, must include letter and number
- **Never stored in plain text**: Only the hash is stored

### JWT Security
- **HS256 signing**: Tokens are cryptographically signed
- **Expiration**: Access tokens expire after 1 hour
- **Refresh tokens**: Get new access token without re-login
- **Blacklist on logout**: Revoked tokens are rejected

### Authorization
- **Role-based**: Different permissions for reader/author/admin
- **Resource ownership**: Authors can only edit their own posts
- **Admin override**: Admins can manage all resources

### Best Practices
- Environment variables for secrets
- Email validation
- Duplicate checking
- Error messages don't leak info
- Account activation/deactivation

## API Endpoints

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Blacklist token
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update profile
- `PUT /auth/me/password` - Change password

### Posts
- `GET /posts` - List posts (public)
- `POST /posts` - Create post (author+)
- `GET /posts/:id` - Get post (public if published)
- `PUT /posts/:id` - Update post (author/admin)
- `DELETE /posts/:id` - Delete post (author/admin)

### Admin
- `GET /admin/users` - List all users (admin)
- `DELETE /admin/users/:id` - Delete user (admin)
- `PATCH /admin/users/:id` - Toggle status (admin)

## Database Schema

### users_auth
```sql
CREATE TABLE users_auth (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'reader',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### posts_auth
```sql
CREATE TABLE posts_auth (
    id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES users_auth(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### token_blacklist_auth
```sql
CREATE TABLE token_blacklist_auth (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(36) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing with curl

### Register
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123",
    "role": "author"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

Save the `access_token` from the response.

### Create Post (authenticated)
```bash
TOKEN="your-access-token-here"

curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Post",
    "content": "This is a test post",
    "is_published": true
  }'
```

### Get Profile
```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### "User not found" after login
- Check if the user was created successfully
- Verify the token is being sent correctly
- Check if the account is active

### "Invalid token" errors
- Token may have expired (1 hour lifetime)
- Use refresh token to get a new access token
- Check if token was blacklisted after logout

### "Requires author role" errors
- Check the user's role in the database
- Ensure you registered with `"role": "author"`
- Readers cannot create posts

### Database connection errors
- Verify `DATABASE_URL` in `.env` is correct
- Check if Supabase database is accessible
- Ensure all tables are created

## Learning Points

This demo teaches:

1. **Password Security**: Never store plain-text passwords
2. **JWT Authentication**: Stateless token-based auth
3. **Authorization**: Role-based access control
4. **Decorators**: Custom Python decorators for auth
5. **Token Lifecycle**: Creation, validation, refresh, revocation
6. **Security Best Practices**: Validation, error handling, environment variables

## Next Steps

After understanding this demo:

1. Complete the exercises in `../exercises/`
2. Try adding more roles (e.g., "moderator")
3. Implement password reset flow
4. Add email verification
5. Implement rate limiting
6. Add two-factor authentication (2FA)

## Resources

- [JWT.io](https://jwt.io/) - Decode and test JWTs
- [bcrypt explained](https://auth0.com/blog/hashing-in-action-understanding-bcrypt/)
- [OWASP Auth Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Flask-JWT-Extended Docs](https://flask-jwt-extended.readthedocs.io/)
