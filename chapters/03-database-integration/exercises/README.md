# Chapter 3 Exercises: Database Integration

## Overview

These exercises progressively teach database integration with Flask, SQLAlchemy, and PostgreSQL (via Supabase). Each exercise builds on the previous one.

**Prerequisites:**
- Completed Chapters 1 and 2
- Supabase database credentials in `.env` file
- Installed: `flask-sqlalchemy`, `psycopg2-binary`, `alembic`, `python-dotenv`

---

## Exercise 1: First Database Model - User Management API

**Objective:** Create your first database-backed API with a single table.

**What You'll Learn:**
- SQLAlchemy model definition
- Database session management
- Basic CRUD operations
- Database migrations (first one!)

**Database Schema:**
```
users
├── id (Integer, Primary Key)
├── username (String 80, Unique, Not Null)
├── email (String 120, Unique, Not Null)
├── full_name (String 100)
├── is_active (Boolean, Default True)
├── created_at (DateTime, Default now)
└── updated_at (DateTime, Default now, onupdate=now)
```

**API Endpoints to Implement:**
- `GET /users` - List all users
- `GET /users/<id>` - Get single user
- `POST /users` - Create user
- `PUT /users/<id>` - Update user
- `DELETE /users/<id>` - Delete user

**TODO Checklist:**
- [ ] Define User model with all fields
- [ ] Set up database connection
- [ ] Implement POST /users (create)
- [ ] Implement GET /users (list all)
- [ ] Implement GET /users/<id> (get one)
- [ ] Implement PUT /users/<id> (update)
- [ ] Implement DELETE /users/<id> (delete)
- [ ] Add validation (unique email, required fields)
- [ ] Handle database errors gracefully

**Success Criteria:**
- ✅ Create a user via POST
- ✅ User appears in Supabase web UI
- ✅ Can retrieve user by ID
- ✅ Can update user's full_name
- ✅ Duplicate email returns 409 Conflict
- ✅ Server restart doesn't lose data

**Test Scenarios:**
```bash
# Create user
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "email": "john@example.com", "full_name": "John Doe"}'

# Get all users
curl http://localhost:5000/users

# Update user
curl -X PUT http://localhost:5000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Smith"}'
```

---

## Exercise 2: One-to-Many Relationships - Blog Posts

**Objective:** Add a Posts table with a foreign key relationship to Users.

**What You'll Learn:**
- Defining relationships in SQLAlchemy
- Foreign keys and cascade deletes
- Nested resource patterns
- Eager vs lazy loading

**Database Schema:**
```
posts
├── id (Integer, Primary Key)
├── user_id (Integer, Foreign Key → users.id)
├── title (String 200, Not Null)
├── content (Text)
├── status (String 20, Default 'draft')  # draft, published, archived
├── view_count (Integer, Default 0)
├── created_at (DateTime)
└── updated_at (DateTime)

Relationship: User ─< Post (one-to-many)
```

**API Endpoints to Implement:**
- `GET /posts` - List all posts
- `GET /posts/<id>` - Get single post
- `POST /posts` - Create post
- `PUT /posts/<id>` - Update post
- `DELETE /posts/<id>` - Delete post
- `GET /users/<id>/posts` - Get all posts by a user (nested resource)

**TODO Checklist:**
- [ ] Define Post model with user_id foreign key
- [ ] Add `posts` relationship to User model
- [ ] Implement all Post CRUD endpoints
- [ ] Implement GET /users/<id>/posts (nested)
- [ ] Add cascade delete (deleting user deletes their posts)
- [ ] Use eager loading to avoid N+1 queries
- [ ] Include author info in post responses

**Success Criteria:**
- ✅ Create post linked to a user
- ✅ GET /posts includes author information
- ✅ GET /users/1/posts returns only that user's posts
- ✅ Deleting a user also deletes their posts
- ✅ Cannot create post with invalid user_id (404)

**Test Scenarios:**
```bash
# Create post
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "title": "My First Post", "content": "Hello world!", "status": "published"}'

# Get user's posts
curl http://localhost:5000/users/1/posts
```

---

## Exercise 3: Multi-tenant Design - Organizations

**Objective:** Implement multi-tenant architecture where data is isolated by organization.

**What You'll Learn:**
- Multi-tenant database patterns
- Tenant isolation
- Query filtering by tenant
- Context-based filtering

**Database Schema:**
```
organizations
├── id (Integer, Primary Key)
├── name (String 100, Unique, Not Null)
├── slug (String 50, Unique, Not Null)
├── plan (String 20, Default 'free')  # free, pro, enterprise
├── created_at (DateTime)
└── is_active (Boolean, Default True)

Modified Users:
├── ... (existing fields)
└── organization_id (Integer, Foreign Key → organizations.id)

Modified Posts:
├── ... (existing fields)
└── organization_id (Integer, Foreign Key → organizations.id)
```

**API Endpoints to Implement:**
- `GET /organizations` - List organizations
- `POST /organizations` - Create organization
- `GET /organizations/<id>` - Get organization
- `GET /organizations/<id>/users` - Get organization's users
- `GET /organizations/<id>/posts` - Get organization's posts

**TODO Checklist:**
- [ ] Create Organization model
- [ ] Add organization_id to User and Post models
- [ ] Implement Organization CRUD endpoints
- [ ] Filter users/posts by organization
- [ ] Prevent cross-organization data access
- [ ] Add organization context to all queries

**Success Criteria:**
- ✅ Create multiple organizations
- ✅ Users/posts belong to organizations
- ✅ GET /organizations/1/posts only returns org 1's posts
- ✅ Cannot access org 2's data via org 1's endpoints

**Test Scenarios:**
```bash
# Create organization
curl -X POST http://localhost:5000/organizations \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp", "slug": "acme", "plan": "pro"}'

# Get organization's posts
curl http://localhost:5000/organizations/1/posts
```

---

## Exercise 4: Database Migrations - Schema Evolution

**Objective:** Learn to manage database schema changes with Alembic.

**What You'll Learn:**
- Alembic setup and configuration
- Creating migrations
- Upgrading and downgrading schema
- Handling data migrations

**Tasks:**

**Part 1: Set up Alembic**
- [ ] Initialize Alembic in the project
- [ ] Configure alembic.ini for Supabase
- [ ] Create initial migration for existing models

**Part 2: Add new columns**
- [ ] Add `bio` (Text) to User model
- [ ] Add `avatar_url` (String) to User model
- [ ] Generate migration
- [ ] Apply migration
- [ ] Verify in Supabase UI

**Part 3: Add new table**
- [ ] Create Category model
- [ ] Add category_id to Post model
- [ ] Generate migration
- [ ] Apply migration

**Part 4: Modify existing column**
- [ ] Change User.username max length from 80 to 50
- [ ] Generate migration
- [ ] Apply migration

**Alembic Commands to Use:**
```bash
# Initialize Alembic
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

**TODO Checklist:**
- [ ] Set up Alembic configuration
- [ ] Create initial migration
- [ ] Add bio and avatar_url columns via migration
- [ ] Create Category table via migration
- [ ] Modify username column via migration
- [ ] Test upgrade and downgrade

**Success Criteria:**
- ✅ `alembic upgrade head` applies all migrations
- ✅ New columns appear in database
- ✅ `alembic downgrade -1` rolls back successfully
- ✅ Can see migration history

---

## Exercise 5: Query Optimization & Audit Logging

**Objective:** Optimize database queries and implement audit trail.

**What You'll Learn:**
- Database indexes
- N+1 query problem and solutions
- Eager loading strategies
- Audit logging patterns
- Soft deletes

**Part 1: Add Indexes**

Add indexes to frequently queried fields:
- [ ] User.email (unique index)
- [ ] User.username (unique index)
- [ ] Post.status (index)
- [ ] Post.created_at (index)
- [ ] Composite index on (organization_id, status)

**Part 2: Fix N+1 Queries**

Current problem:
```python
# ❌ Bad: N+1 queries
posts = Post.query.all()  # 1 query
for post in posts:
    print(post.author.username)  # N queries (one per post!)
```

TODO:
- [ ] Use `joinedload()` for author relationship
- [ ] Use `selectinload()` for posts relationship
- [ ] Add query debugging to see SQL

**Part 3: Implement Audit Logging**

Create AuditLog table:
```
audit_logs
├── id (Integer, Primary Key)
├── user_id (Integer, Foreign Key)
├── action (String 50)  # create, update, delete
├── table_name (String 50)
├── record_id (Integer)
├── old_values (JSON, nullable)
├── new_values (JSON)
├── ip_address (String 45, nullable)
├── created_at (DateTime)
```

TODO:
- [ ] Create AuditLog model
- [ ] Add audit logging to User CRUD
- [ ] Add audit logging to Post CRUD
- [ ] Capture old and new values
- [ ] Store IP address from request

**Part 4: Soft Deletes**

Instead of actually deleting records, mark them as deleted:
- [ ] Add `deleted_at` column to User and Post
- [ ] Modify DELETE endpoints to set deleted_at
- [ ] Filter out soft-deleted records in queries
- [ ] Add `/users/<id>/restore` endpoint

**TODO Checklist:**
- [ ] Add database indexes
- [ ] Fix N+1 queries with eager loading
- [ ] Create AuditLog model
- [ ] Implement audit logging for all CRUD
- [ ] Implement soft delete for User and Post
- [ ] Add restore endpoint

**Success Criteria:**
- ✅ Queries run faster with indexes
- ✅ No N+1 queries (check SQL logs)
- ✅ All CRUD operations logged to audit_logs table
- ✅ Soft-deleted users don't appear in GET /users
- ✅ Can restore soft-deleted users

**Test Scenarios:**
```bash
# Check audit logs
curl http://localhost:5000/audit-logs

# Soft delete user
curl -X DELETE http://localhost:5000/users/1

# Verify user hidden
curl http://localhost:5000/users  # Should not include user 1

# Restore user
curl -X POST http://localhost:5000/users/1/restore
```

---

## Running the Exercises

### Setup

1. **Install dependencies:**
   ```bash
   pip install flask-sqlalchemy psycopg2-binary alembic python-dotenv flask-restx flask-cors
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Run each exercise:**
   ```bash
   cd exercises/exercise_1_first_model
   python app.py
   ```

### Checking Your Work

1. **Swagger UI:** http://localhost:5000/swagger
2. **Supabase UI:** Check tables and data in Supabase dashboard
3. **Test with curl or Postman**

---

## Common Issues & Solutions

### Issue: "relation does not exist"
**Solution:** Run migrations or create tables:
```python
db.create_all()  # Creates all tables
```

### Issue: "SQLALCHEMY_TRACK_MODIFICATIONS warning"
**Solution:** Set in config:
```python
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

### Issue: "password authentication failed"
**Solution:** Check your `.env` DATABASE_URL is correct

### Issue: Changes not saved
**Solution:** Remember to commit!
```python
db.session.commit()
```

---

## Progress Checklist

- [ ] Exercise 1: First Database Model ✅
- [ ] Exercise 2: One-to-Many Relationships ✅
- [ ] Exercise 3: Multi-tenant Design ✅
- [ ] Exercise 4: Database Migrations ✅
- [ ] Exercise 5: Query Optimization & Audit Logging ✅

---

**Next Chapter:** Chapter 4 - Authentication & Authorization (JWT, OAuth2, role-based access control)
