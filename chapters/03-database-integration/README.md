# Chapter 3: Database Integration with PostgreSQL & Supabase

## What You'll Learn

This chapter teaches you how to connect Flask APIs to a real PostgreSQL database using SQLAlchemy ORM and Supabase as your database host.

**Key Topics:**
- Understanding databases and why we need them
- SQLAlchemy ORM basics (no raw SQL needed!)
- Database models and relationships
- Migrations with Alembic
- Multi-tenant architecture
- Query optimization and best practices

---

## Why Do We Need Databases?

### The Problem with In-Memory Storage

In Chapters 1 and 2, we stored data in Python lists:

```python
users = []  # This disappears when the server restarts!
```

**Problems:**
- ❌ Data lost on server restart
- ❌ Can't handle large datasets
- ❌ No data validation or integrity
- ❌ Slow searches and queries
- ❌ Can't share data across servers

### The Database Solution

```python
# With a database, data is persistent and queryable
user = db.session.query(User).filter_by(email='john@example.com').first()
```

**Benefits:**
- ✅ Data persists across restarts
- ✅ Handles millions of records
- ✅ Data validation and relationships
- ✅ Fast indexed queries
- ✅ Concurrent access by multiple servers

---

## What is PostgreSQL?

**PostgreSQL** is a powerful, open-source relational database. Think of it as an Excel spreadsheet on steroids:

| Feature | Excel | PostgreSQL |
|---------|-------|------------|
| Size limit | ~1M rows | Billions of rows |
| Speed | Slow on large data | Fast with indexes |
| Concurrent users | 1-2 | Thousands |
| Relationships | Manual | Automatic (foreign keys) |
| Data types | Limited | Rich (JSON, arrays, etc.) |
| ACID guarantees | No | Yes |

**Why PostgreSQL?**
- Industry standard (used by Instagram, Spotify, Reddit)
- Rich data types (JSON, arrays, ranges)
- Excellent documentation
- Strong ecosystem
- Free and open-source

---

## What is Supabase?

**Supabase** is "Firebase for PostgreSQL" - it hosts your PostgreSQL database in the cloud.

**Why use Supabase for this tutorial?**
- ✅ No local installation needed
- ✅ Free tier (500MB database)
- ✅ Web UI to view your data
- ✅ Automatic backups
- ✅ Built-in authentication (we'll use in Chapter 4)
- ✅ Works from anywhere

**It's just PostgreSQL!** Anything you learn here works with any PostgreSQL database (AWS RDS, Google Cloud SQL, self-hosted, etc.).

---

## What is an ORM?

**ORM** = Object-Relational Mapping

### Without ORM (Raw SQL):

```python
# Hard to maintain, error-prone
cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
```

### With ORM (SQLAlchemy):

```python
# Clean, Pythonic, type-safe
user = User(name="John", email="john@example.com")
db.session.add(user)
db.session.commit()
```

**Benefits of using SQLAlchemy ORM:**
- ✅ Write Python instead of SQL
- ✅ Type safety and autocomplete
- ✅ Prevents SQL injection
- ✅ Database-agnostic (switch from PostgreSQL to MySQL easily)
- ✅ Automatic relationship loading
- ✅ Query composition and reuse

---

## Database Concepts for Beginners

### 1. Tables (like classes)

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
```

This creates a table:

| id | name | email |
|----|------|-------|
| 1  | John | john@example.com |
| 2  | Jane | jane@example.com |

### 2. Relationships (connections between tables)

**One-to-Many:** One user can have many posts

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship('Post', backref='author')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

**Many-to-Many:** One post can have many tags, one tag can be on many posts

```python
tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)
```

### 3. Migrations (database version control)

When you change your models, you need to update the database schema:

```bash
# Create a migration
alembic revision --autogenerate -m "Add user table"

# Apply the migration
alembic upgrade head
```

Think of migrations like Git commits for your database structure.

### 4. Indexes (make queries fast)

Without index: Search 1 million users = check all 1 million rows
With index: Search 1 million users = check ~20 rows

```python
class User(db.Model):
    email = db.Column(db.String(100), unique=True, index=True)  # ← Fast lookups!
```

---

## Chapter Structure

### Demo Project: Multi-tenant Blog Platform

A complete blogging platform with:
- Organizations (tenants)
- Users belonging to organizations
- Posts with authors
- Comments on posts
- Categories and tags
- Audit logging

**You'll see:**
- Complete database schema design
- All relationship types
- Query optimization
- Migration management

### Exercises

**Exercise 1: First Database Model**
- Create User table with basic CRUD
- Learn SQLAlchemy basics
- Understand sessions and commits

**Exercise 2: One-to-Many Relationships**
- Add Posts table linked to Users
- Foreign keys and relationships
- Cascade deletes
- Eager vs lazy loading

**Exercise 3: Multi-tenant Design**
- Add Organizations table
- Tenant isolation patterns
- Filtered queries

**Exercise 4: Database Migrations**
- Set up Alembic
- Create and apply migrations
- Handle schema changes
- Rollback strategies

**Exercise 5: Query Optimization & Audit Logging**
- Add database indexes
- Prevent N+1 queries
- Implement audit trail
- Soft deletes

---

## Prerequisites

Before starting this chapter:

1. **Supabase Account & Database**
   - Your instructor will provide database credentials
   - You'll receive a `DATABASE_URL` connection string

2. **Install Dependencies**
   ```bash
   pip install flask-sqlalchemy psycopg2-binary alembic python-dotenv
   ```

3. **Environment Setup**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials

---

## Key Takeaways

By the end of this chapter, you'll understand:

✅ **Why databases are essential** for production applications
✅ **How ORMs work** and why they're better than raw SQL
✅ **Database relationships** (one-to-many, many-to-many)
✅ **Migration management** for schema changes
✅ **Multi-tenant patterns** for SaaS applications
✅ **Query optimization** to avoid performance issues

---

## Common Beginner Mistakes

### ❌ Forgetting to commit

```python
user = User(name="John")
db.session.add(user)
# ❌ Missing db.session.commit() - changes not saved!
```

### ❌ N+1 Query Problem

```python
# ❌ Bad: Runs 1 + N queries
users = User.query.all()
for user in users:
    print(user.posts)  # Each iteration queries the database!

# ✅ Good: Runs 1 query
users = User.query.options(joinedload(User.posts)).all()
```

### ❌ Not using relationships

```python
# ❌ Bad: Manual joins
user_id = 5
posts = Post.query.filter_by(user_id=user_id).all()

# ✅ Good: Use relationships
user = User.query.get(5)
posts = user.posts  # SQLAlchemy handles the join
```

### ❌ Exposing database IDs in URLs without validation

```python
# ❌ Bad: No validation
@app.route('/users/<int:id>')
def get_user(id):
    return User.query.get(id)  # What if id doesn't exist?

# ✅ Good: Handle missing records
@app.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return user
```

---

## Database Design Principles

### 1. Normalize your data (avoid duplication)

❌ **Bad: Duplicated data**
```
Posts Table:
| id | title | author_name | author_email |
|----|-------|-------------|--------------|
| 1  | Post1 | John        | john@ex.com  |
| 2  | Post2 | John        | john@ex.com  | ← Duplicated!
```

✅ **Good: Normalized with relationships**
```
Users Table:
| id | name | email       |
|----|------|-------------|
| 1  | John | john@ex.com |

Posts Table:
| id | title | user_id |
|----|-------|---------|
| 1  | Post1 | 1       |
| 2  | Post2 | 1       |
```

### 2. Use appropriate data types

```python
# ✅ Good
created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Not String!
price = db.Column(db.Numeric(10, 2))  # Not Float for money!
is_active = db.Column(db.Boolean, default=True)  # Not Integer!
```

### 3. Add constraints

```python
email = db.Column(db.String(100), unique=True, nullable=False)  # ← Constraints
```

---

## Quick Reference: SQLAlchemy Commands

### Creating Records
```python
user = User(name="John", email="john@example.com")
db.session.add(user)
db.session.commit()
```

### Reading Records
```python
# Get by ID
user = User.query.get(1)

# Get all
users = User.query.all()

# Filter
user = User.query.filter_by(email="john@example.com").first()

# Complex queries
users = User.query.filter(User.age > 18).order_by(User.name).limit(10).all()
```

### Updating Records
```python
user = User.query.get(1)
user.name = "John Smith"
db.session.commit()
```

### Deleting Records
```python
user = User.query.get(1)
db.session.delete(user)
db.session.commit()
```

---

## Next Steps

1. Read through the **demo project** (`demo/app.py`)
2. Complete **exercises 1-5** in order
3. Experiment with Supabase web UI to see your data
4. Move on to **Chapter 4: Authentication** to add user login

---

**Remember:** Databases seem complex at first, but they're just organized storage. Take it step by step, and soon it will feel natural!
