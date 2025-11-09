# Demo: Multi-tenant Blog Platform API

This demo showcases a **production-ready** blog platform API with all the best practices from Chapter 3.

## What's Included

✅ **Multi-tenant Architecture** - Multiple organizations with isolated data
✅ **Complete CRUD** - All operations for organizations, users, and posts
✅ **Audit Logging** - Track who changed what and when (compliance-ready)
✅ **Soft Deletes** - Mark records as deleted instead of actually deleting them
✅ **Query Optimization** - Indexes and eager loading to prevent N+1 queries
✅ **Proper Error Handling** - Validation and meaningful error messages
✅ **Swagger Documentation** - Interactive API documentation

## Architecture

```
Organizations (Tenants)
    ├── Users
    │   └── Posts
    └── Posts

AuditLogs (tracks all changes)
```

**Real-world example:** Like Slack or Notion
- Organization = A company or team
- Users = Members of that organization
- Posts = Content created by those users
- Audit Logs = History of all changes

## Database Schema

### organizations
```
id              INTEGER PRIMARY KEY
name            VARCHAR(100) UNIQUE NOT NULL
slug            VARCHAR(50) UNIQUE NOT NULL
plan            VARCHAR(20) DEFAULT 'free'
is_active       BOOLEAN DEFAULT TRUE
created_at      TIMESTAMP
updated_at      TIMESTAMP
deleted_at      TIMESTAMP (for soft deletes)

Indexes:
- name (unique)
- slug (unique)
- (is_active, plan) composite
```

### users
```
id              INTEGER PRIMARY KEY
username        VARCHAR(80) UNIQUE NOT NULL
email           VARCHAR(120) UNIQUE NOT NULL
full_name       VARCHAR(100)
is_active       BOOLEAN DEFAULT TRUE
organization_id INTEGER FK → organizations.id
created_at      TIMESTAMP
updated_at      TIMESTAMP
deleted_at      TIMESTAMP

Indexes:
- username (unique)
- email (unique)
- organization_id
- (organization_id, is_active) composite
```

### posts
```
id              INTEGER PRIMARY KEY
user_id         INTEGER FK → users.id
organization_id INTEGER FK → organizations.id
title           VARCHAR(200) NOT NULL
content         TEXT
status          VARCHAR(20) DEFAULT 'draft'
view_count      INTEGER DEFAULT 0
created_at      TIMESTAMP
updated_at      TIMESTAMP
deleted_at      TIMESTAMP

Indexes:
- user_id
- organization_id
- status
- (organization_id, status) composite
- (organization_id, created_at) composite
```

### audit_logs
```
id              INTEGER PRIMARY KEY
user_id         INTEGER FK → users.id (who made the change)
action          VARCHAR(50) NOT NULL (create/update/delete)
table_name      VARCHAR(50) NOT NULL
record_id       INTEGER NOT NULL (which record was affected)
old_values      TEXT (JSON - data before change)
new_values      TEXT (JSON - data after change)
ip_address      VARCHAR(45)
created_at      TIMESTAMP

Indexes:
- action
- table_name
- record_id
- (table_name, record_id) composite
```

## Running the Demo

### 1. Install Dependencies

```bash
pip install flask flask-restx flask-sqlalchemy flask-cors psycopg2-binary python-dotenv
```

### 2. Configure Environment

Make sure your `.env` file in `chapters/03-database-integration/` has:

```bash
DATABASE_URL="postgresql://..."
DIRECT_URL="postgresql://..."
```

### 3. Run the Application

```bash
cd chapters/03-database-integration/demo
python app.py
```

### 4. Access Swagger UI

Open http://localhost:5000/swagger in your browser

## Demo Walkthrough

### Step 1: Create an Organization

```bash
POST http://localhost:5000/organizations

{
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "plan": "pro"
}

Response: 201 Created
{
  "id": 1,
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "plan": "pro",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  ...
}
```

### Step 2: Create Users

```bash
POST http://localhost:5000/users

{
  "username": "alice",
  "email": "alice@acme.com",
  "full_name": "Alice Johnson",
  "organization_id": 1
}
```

Create another user:

```bash
POST http://localhost:5000/users

{
  "username": "bob",
  "email": "bob@acme.com",
  "full_name": "Bob Smith",
  "organization_id": 1
}
```

### Step 3: Create Posts

```bash
POST http://localhost:5000/posts

{
  "user_id": 1,
  "organization_id": 1,
  "title": "Welcome to Acme!",
  "content": "This is our first blog post...",
  "status": "published"
}
```

### Step 4: List Posts (See Eager Loading in Action!)

```bash
GET http://localhost:5000/posts

Response:
[
  {
    "id": 1,
    "title": "Welcome to Acme!",
    "author": {
      "id": 1,
      "username": "alice",
      "email": "alice@acme.com"
    }
  }
]
```

**Note:** Check the terminal logs. You'll see **only 1 SQL query** instead of 2 (post + author). This is thanks to `joinedload()` preventing the N+1 problem!

### Step 5: View Audit Logs

```bash
GET http://localhost:5000/audit-logs

Response:
[
  {
    "id": 3,
    "action": "create",
    "table_name": "posts",
    "record_id": 1,
    "user_id": 1,
    "new_values": {
      "id": 1,
      "title": "Welcome to Acme!",
      ...
    },
    "created_at": "2024-01-15T10:35:00"
  },
  {
    "id": 2,
    "action": "create",
    "table_name": "users",
    "record_id": 2,
    ...
  }
]
```

### Step 6: Soft Delete a User

```bash
DELETE http://localhost:5000/users/1

Response: 204 No Content
```

Verify user is hidden:

```bash
GET http://localhost:5000/users

Response: [] (user 1 not included)
```

But check Supabase - the user row still exists with `deleted_at` set!

### Step 7: Restore the User

```bash
POST http://localhost:5000/users/1/restore

Response: 200 OK
{
  "id": 1,
  "username": "alice",
  "deleted_at": null,
  ...
}
```

### Step 8: Multi-Tenant Isolation

Create a second organization:

```bash
POST http://localhost:5000/organizations
{
  "name": "Tech Inc",
  "slug": "tech-inc",
  "plan": "free"
}
```

Create a user in the new org:

```bash
POST http://localhost:5000/users
{
  "username": "charlie",
  "email": "charlie@tech.com",
  "organization_id": 2
}
```

Now filter by organization:

```bash
GET http://localhost:5000/organizations/1/users
# Returns only Alice and Bob

GET http://localhost:5000/organizations/2/users
# Returns only Charlie
```

**This is tenant isolation!** Each organization's data is completely separate.

## Key Features Explained

### 1. Audit Logging

Every create, update, and delete operation is logged:

```python
log_audit(
    user_id=1,
    action='update',
    table_name='posts',
    record_id=5,
    old_values={'title': 'Old Title'},
    new_values={'title': 'New Title'}
)
```

**Use cases:**
- Compliance (GDPR, SOC2, HIPAA)
- Debugging ("Who changed this?")
- Security (detect unauthorized access)
- Analytics (user behavior)

### 2. Soft Deletes

Instead of:
```python
db.session.delete(user)  # ❌ Data lost forever!
```

We do:
```python
user.deleted_at = datetime.utcnow()  # ✅ Recoverable!
```

**Benefits:**
- Data recovery (restore accidentally deleted records)
- Audit trail preservation
- Cascading delete handling
- Historical data analysis

### 3. Query Optimization

#### Indexes

```python
# Single column index
email = db.Column(db.String(120), index=True)

# Composite index for common query patterns
__table_args__ = (
    Index('idx_post_org_status', 'organization_id', 'status'),
)
```

**Why?** Searching 1 million posts for `organization_id=5 AND status='published'` is **1000x faster** with the composite index!

#### Eager Loading (N+1 Prevention)

```python
# ❌ Bad: N+1 queries
posts = Post.query.all()  # 1 query
for post in posts:
    print(post.author.username)  # N additional queries!

# ✅ Good: 1 query
posts = Post.query.options(joinedload(Post.author)).all()  # 1 query with JOIN
for post in posts:
    print(post.author.username)  # No additional queries!
```

### 4. Multi-Tenant Architecture

**Pattern:** Shared database, isolated data

```python
# All models have organization_id
organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)

# All queries filter by organization
posts = Post.query.filter_by(organization_id=current_org_id).all()
```

**Real-world applications:**
- Slack (each workspace is a tenant)
- Asana (each team is a tenant)
- Shopify (each store is a tenant)

## Testing Multi-Tenancy

### Test Data Isolation

1. Create Org A and Org B
2. Create users in each org
3. Create posts in each org
4. Try to access Org A's posts from Org B → Should fail or return empty

### Test Cross-Organization Validation

```bash
# Create user in Org 1
POST /users
{
  "username": "alice",
  "organization_id": 1
}

# Try to create post by alice in Org 2 (should fail!)
POST /posts
{
  "user_id": 1,  # alice
  "organization_id": 2  # Different org!
}

Response: 400 Bad Request
{
  "message": "User does not belong to this organization"
}
```

## Production Considerations

### 1. Authentication

This demo doesn't include authentication. In production, you would:

```python
# Get current user from JWT token
current_user = get_current_user_from_token()

# Automatically set organization_id
organization_id = current_user.organization_id

# Filter all queries
posts = Post.query.filter_by(organization_id=current_user.organization_id).all()
```

### 2. Pagination

For large datasets, add pagination:

```python
page = request.args.get('page', 1, type=int)
per_page = 20

posts = Post.query.paginate(page=page, per_page=per_page)

return {
    'items': [post.to_dict() for post in posts.items],
    'total': posts.total,
    'pages': posts.pages,
    'page': page
}
```

### 3. Rate Limiting

Prevent abuse:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@limiter.limit("100 per hour")
@app.route('/posts')
def list_posts():
    ...
```

### 4. Caching

For frequently accessed data:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def get_organization_stats(org_id):
    ...
```

### 5. Background Jobs

For heavy operations (like sending emails):

```python
from celery import Celery

@celery.task
def send_notification_email(user_id, post_id):
    ...
```

## SQL Query Debugging

Uncomment this line in `app.py`:

```python
app.config['SQLALCHEMY_ECHO'] = True
```

Now you'll see all SQL queries in the terminal:

```sql
SELECT posts.id, posts.title, users.id, users.username
FROM posts
LEFT OUTER JOIN users ON users.id = posts.user_id
WHERE posts.deleted_at IS NULL
```

**Use this to:**
- Identify N+1 queries
- Verify indexes are being used
- Debug slow queries
- Learn SQL!

## Common Issues

### Issue: Duplicate key error

```
IntegrityError: duplicate key value violates unique constraint "users_email_key"
```

**Solution:** This is intentional! The unique constraint prevents duplicate emails. Handle it gracefully:

```python
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    return {'message': 'Email already exists'}, 409
```

### Issue: Foreign key violation

```
IntegrityError: insert or update on table "posts" violates foreign key constraint
```

**Solution:** Always validate foreign keys exist before creating records:

```python
user = User.query.get(data['user_id'])
if not user:
    return {'message': 'User not found'}, 404
```

## Next Steps

After exploring this demo:

1. **Try the exercises** - Build your own version from scratch
2. **Add features** - Comments, tags, likes, etc.
3. **Implement authentication** - Use Flask-JWT-Extended
4. **Deploy to production** - Use Gunicorn + Nginx
5. **Add tests** - Use pytest to test your API

## Further Reading

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy Quickstart](https://flask-sqlalchemy.palletsprojects.com/)
- [Multi-Tenancy Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/multitenancy)
- [Database Indexing](https://use-the-index-luke.com/)
- [GDPR Compliance](https://gdpr.eu/)
