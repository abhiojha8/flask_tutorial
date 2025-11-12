# Unified Backend API for Streamlit Frontend

This is a complete Flask REST API that combines concepts from Chapters 1-5, serving as the backend for the Streamlit frontend demo.

## Features

- ✅ **RESTful API Design** (Chapter 2) - Proper resource endpoints, HTTP methods, status codes
- ✅ **Database Integration** (Chapter 3) - PostgreSQL with SQLAlchemy ORM
- ✅ **JWT Authentication** (Chapter 4) - Secure user registration, login, protected routes
- ✅ **Data Validation** (Chapter 5) - Marshmallow schemas with custom validators
- ✅ **File Upload** - Image upload with validation
- ✅ **CORS Enabled** - For frontend integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your DATABASE_URL from previous chapters
# Or use a new PostgreSQL database
```

### 3. Run the Application

```bash
python app.py
```

The API will be available at:
- Base URL: `http://localhost:5000/api`
- Swagger UI: `http://localhost:5000/swagger`

## Sample Data

The application automatically creates sample data on first run:

**Users:**
- Email: `john@example.com` / Password: `Password123!`
- Email: `jane@example.com` / Password: `Password123!`

**Articles:** 3 sample articles with different categories
**Comments:** 2 sample comments on first article

## API Endpoints

### Authentication

```
POST   /api/auth/register     - Register new user
POST   /api/auth/login        - Login and get JWT token
GET    /api/auth/me           - Get current user (requires auth)
POST   /api/auth/logout       - Logout (blacklist token)
```

### Articles

```
GET    /api/articles          - List articles (with filters)
POST   /api/articles          - Create article (requires auth)
GET    /api/articles/{id}     - Get single article
PUT    /api/articles/{id}     - Update article (requires auth + ownership)
DELETE /api/articles/{id}     - Delete article (requires auth + ownership)
POST   /api/articles/{id}/image - Upload image (requires auth + ownership)
```

**Query Parameters for GET /api/articles:**
- `search` - Search in title/content
- `category` - Filter by category
- `published` - Filter by published status (true/false)
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)

Example:
```
GET /api/articles?published=true&category=Technology&page=1&per_page=10
```

### Comments

```
GET    /api/articles/{id}/comments  - Get article comments
POST   /api/articles/{id}/comments  - Add comment to article
```

### Authors

```
GET    /api/authors              - List all authors
GET    /api/authors/{id}         - Get author details
GET    /api/authors/{id}/articles - Get author's articles
```

## Using with Streamlit Frontend

1. **Start this backend:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start Streamlit frontend (in another terminal):**
   ```bash
   cd demo_2_blog_frontend
   streamlit run app.py
   ```

3. **The frontend will connect to** `http://localhost:5000/api`

## Testing with curl

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "Password123!"
  }'
```

Save the token from the response!

### Get Articles
```bash
curl http://localhost:5000/api/articles
```

### Create Article (with auth)
```bash
curl -X POST http://localhost:5000/api/articles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "My New Article",
    "content": "This is the content of my article. It must be at least 50 characters long to pass validation.",
    "category": "Technology",
    "tags": ["python", "tutorial"],
    "published": true
  }'
```

### Add Comment
```bash
curl -X POST http://localhost:5000/api/articles/1/comments \
  -H "Content-Type: application/json" \
  -d '{
    "author_name": "Commenter",
    "author_email": "commenter@example.com",
    "text": "Great article!"
  }'
```

## Database Schema

```sql
-- Users
CREATE TABLE users_frontend (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Articles
CREATE TABLE articles_frontend (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    slug VARCHAR(250) UNIQUE,
    author_id INTEGER REFERENCES users_frontend(id),
    category VARCHAR(50),
    tags JSONB,
    published BOOLEAN DEFAULT FALSE,
    views INTEGER DEFAULT 0,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Comments
CREATE TABLE comments_frontend (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles_frontend(id),
    author_name VARCHAR(50) NOT NULL,
    author_email VARCHAR(120) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Token Blacklist (for logout)
CREATE TABLE token_blacklist_frontend (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(120) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Validation Rules

### User Registration
- Username: 3-50 chars, alphanumeric + underscore, must start with letter
- Email: Valid email format, unique
- Password: Min 8 chars, must have uppercase, lowercase, number, special char
- Bio: Max 500 chars (optional)

### Article Creation
- Title: 5-200 chars
- Content: Min 50 chars
- Category: One of [Technology, Science, Business, Health, Sports]
- Tags: Max 10 tags, each max 20 chars, must be unique
- Published: Boolean (default: false)

### Comment Creation
- Author Name: 2-50 chars
- Author Email: Valid email
- Text: 1-1000 chars

### File Upload
- Size: Max 5MB
- Types: jpg, jpeg, png, gif
- Validated with PIL to ensure it's actually an image

## Error Responses

All errors return JSON with appropriate status codes:

**400 Bad Request** - Validation errors
```json
{
  "errors": {
    "title": ["Length must be between 5 and 200."],
    "password": ["Password must contain at least one uppercase letter"]
  }
}
```

**401 Unauthorized** - Invalid credentials or expired token
```json
{
  "message": "Invalid email or password"
}
```

**403 Forbidden** - Not authorized to perform action
```json
{
  "message": "Not authorized"
}
```

**404 Not Found** - Resource doesn't exist
```json
{
  "message": "Article not found"
}
```

## Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT tokens with expiration
- ✅ Token blacklist for logout
- ✅ Input validation with Marshmallow
- ✅ File upload validation
- ✅ CORS configuration
- ✅ SQL injection prevention (SQLAlchemy)

## Notes

- Tables use `_frontend` suffix to avoid conflicts with other chapters
- JWT tokens expire after 1 hour (access) and 30 days (refresh)
- File uploads are saved to `uploads/` directory
- Sample data is created automatically on first run
- All timestamps are in UTC

## Troubleshooting

**"DATABASE_URL not found"**
- Make sure you have a `.env` file with `DATABASE_URL` set

**"Cannot connect to database"**
- Check your PostgreSQL connection string
- Ensure the database server is running

**"Token has expired"**
- Login again to get a new token
- Tokens expire after 1 hour

**"CORS error from frontend"**
- CORS is already enabled for all origins
- Make sure backend is running on port 5000

## Next Steps

After starting this backend:
1. Explore the Swagger UI at `http://localhost:5000/swagger`
2. Test endpoints with curl or Postman
3. Start the Streamlit frontend to see full-stack integration
4. Complete the exercises to build your own frontend features

---

**This backend is production-ready** with proper validation, authentication, and error handling! 🚀
