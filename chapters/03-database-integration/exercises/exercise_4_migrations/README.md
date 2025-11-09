# Exercise 4: Database Migrations with Alembic

## OBJECTIVE

Learn to manage database schema changes using Alembic, the migration tool for SQLAlchemy. This is essential for production applications where you can't just drop and recreate tables!

## WHAT YOU'LL LEARN

- Setting up Alembic in a Flask project
- Creating migration files
- Applying migrations (upgrade)
- Rolling back migrations (downgrade)
- Handling schema changes (add columns, modify columns, add tables)
- Managing migration history

## WHY MIGRATIONS?

### The Problem Without Migrations

```python
# ❌ Bad: Just recreating tables loses all data!
db.drop_all()
db.create_all()  # All your data is gone!
```

### The Solution With Migrations

```bash
# ✅ Good: Migrations evolve your schema without losing data
alembic upgrade head  # Applies changes while preserving existing data
```

**Real-world scenario:**
- Your app is running in production with 10,000 users
- You need to add a `phone_number` column to the users table
- You CAN'T drop the table (you'd lose 10,000 users!)
- Solution: Create a migration that adds the column

## MIGRATIONS ARE LIKE GIT FOR YOUR DATABASE

| Git | Alembic |
|-----|---------|
| git commit | alembic revision |
| git log | alembic history |
| git checkout | alembic upgrade/downgrade |
| .git/ folder | alembic/ folder |
| commit messages | migration descriptions |

## EXERCISE TASKS

### Part 1: Set Up Alembic

**Step 1: Install Alembic**
```bash
pip install alembic
```

**Step 2: Initialize Alembic**
```bash
# From the exercise_4_migrations directory
alembic init alembic
```

This creates:
```
exercise_4_migrations/
├── alembic/
│   ├── versions/       # Migration files go here
│   ├── env.py          # Alembic environment configuration
│   ├── script.py.mako  # Migration template
│   └── README
├── alembic.ini         # Main configuration file
└── app.py             # Your Flask app
```

**Step 3: Configure Alembic**

You need to tell Alembic:
1. Where your database is (connection string)
2. Where your models are (so it can detect changes)

**TODO: Edit `alembic.ini`**

Find this line:
```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

Replace with:
```ini
# Comment it out - we'll set it in env.py instead
# sqlalchemy.url =
```

**TODO: Edit `alembic/env.py`**

Add at the top (after imports):
```python
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Import your models
from app import db

# Set target metadata for autogenerate
target_metadata = db.Model.metadata
```

Find the `run_migrations_offline()` function and update:
```python
def run_migrations_offline():
    url = os.getenv('DIRECT_URL')  # Use DIRECT_URL for migrations
    # ... rest of the function
```

Find the `run_migrations_online()` function and update:
```python
def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = os.getenv('DIRECT_URL')
    # ... rest of the function
```

**Why DIRECT_URL?**
- `DATABASE_URL` (pooled connection) → Use in your app for queries
- `DIRECT_URL` (direct connection) → Use for migrations (Alembic requirement)

### Part 2: Create Initial Migration

**Step 1: Create migration**
```bash
alembic revision --autogenerate -m "Initial schema - users, posts, organizations"
```

This creates a file like `alembic/versions/abc123_initial_schema.py`

**Step 2: Review the migration**

Open the generated file. You'll see:
```python
def upgrade():
    # Creates tables
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), nullable=False),
        # ... more columns
    )

def downgrade():
    # Drops tables (for rollback)
    op.drop_table('users')
```

**Step 3: Apply the migration**
```bash
alembic upgrade head
```

**Step 4: Check migration history**
```bash
alembic current  # Shows current version
alembic history  # Shows all migrations
```

### Part 3: Add New Columns

**Scenario:** You want to add `bio` and `avatar_url` to the User model.

**Step 1: Modify the model in app.py**

```python
class User(db.Model):
    # ... existing fields ...
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
```

**Step 2: Generate migration**
```bash
alembic revision --autogenerate -m "Add bio and avatar_url to users"
```

**Step 3: Review generated migration**

Alembic detected your changes!
```python
def upgrade():
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')
```

**Step 4: Apply migration**
```bash
alembic upgrade head
```

**Step 5: Verify in Supabase UI**

Check the users table - you should see the new columns!

### Part 4: Add New Table

**Scenario:** Add a Category table for blog posts.

**Step 1: Add Category model to app.py**

```python
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to posts
    posts = db.relationship('Post', backref='category', lazy=True)
```

**Step 2: Add category_id to Post model**

```python
class Post(db.Model):
    # ... existing fields ...
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
```

**Step 3: Generate migration**
```bash
alembic revision --autogenerate -m "Add categories table and category_id to posts"
```

**Step 4: Apply migration**
```bash
alembic upgrade head
```

### Part 5: Modify Existing Column

**Scenario:** Change User.username max length from 80 to 50.

**Step 1: Modify model**
```python
class User(db.Model):
    username = db.Column(db.String(50), unique=True, nullable=False)  # Changed from 80
```

**Step 2: Generate migration**
```bash
alembic revision --autogenerate -m "Reduce username max length to 50"
```

**⚠️ WARNING:** Alembic might NOT detect this change automatically!

You may need to manually write the migration:
```python
def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('username',
                              existing_type=sa.String(80),
                              type_=sa.String(50))

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('username',
                              existing_type=sa.String(50),
                              type_=sa.String(80))
```

**Step 3: Apply migration**
```bash
alembic upgrade head
```

### Part 6: Rollback (Downgrade)

**Scenario:** You made a mistake and want to undo the last migration.

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to a specific version
alembic downgrade abc123

# Rollback everything
alembic downgrade base
```

**Check current version after rollback:**
```bash
alembic current
```

## COMMON ALEMBIC COMMANDS

```bash
# Initialize Alembic
alembic init alembic

# Create a migration (autogenerate from model changes)
alembic revision --autogenerate -m "Description"

# Create an empty migration (for manual edits)
alembic revision -m "Description"

# Apply all pending migrations
alembic upgrade head

# Apply migrations up to a specific version
alembic upgrade abc123

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base

# Show current version
alembic current

# Show migration history
alembic history

# Show detailed history with diffs
alembic history --verbose
```

## TODO CHECKLIST

- [ ] Install Alembic: `pip install alembic`
- [ ] Initialize Alembic: `alembic init alembic`
- [ ] Configure `alembic.ini` (comment out sqlalchemy.url)
- [ ] Configure `alembic/env.py` (add model imports and DIRECT_URL)
- [ ] Create initial migration for existing models
- [ ] Apply initial migration: `alembic upgrade head`
- [ ] Add `bio` and `avatar_url` columns to User model
- [ ] Generate and apply migration for new columns
- [ ] Add Category model and category_id to Post
- [ ] Generate and apply migration for Category table
- [ ] (Optional) Modify username max length
- [ ] (Optional) Generate and apply column modification migration
- [ ] Test rollback: `alembic downgrade -1`
- [ ] Test re-applying: `alembic upgrade head`
- [ ] Verify all changes in Supabase UI

## SUCCESS CRITERIA

✅ `alembic upgrade head` runs without errors
✅ New columns appear in Supabase users table
✅ Category table created in Supabase
✅ `alembic current` shows the latest migration
✅ `alembic history` shows all your migrations
✅ `alembic downgrade -1` successfully rolls back
✅ Database matches your model definitions

## COMMON ISSUES

### Issue: "Can't locate revision identified by 'abc123'"
**Solution:** Make sure you're in the correct directory and alembic/ folder exists.

### Issue: "Target database is not up to date"
**Solution:** Run `alembic upgrade head` first.

### Issue: Migration creates duplicate tables
**Solution:** Check if tables already exist. You might need to stamp the database:
```bash
alembic stamp head  # Mark current state as up-to-date without running migrations
```

### Issue: Alembic doesn't detect my model changes
**Solution:**
1. Make sure you imported the model in `alembic/env.py`
2. Some changes (like column type modifications) need manual migrations

### Issue: "SQLALCHEMY_DATABASE_URI is not set"
**Solution:** Make sure you're loading environment variables in `alembic/env.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## PRODUCTION BEST PRACTICES

1. **Always review generated migrations** - Alembic isn't perfect
2. **Test migrations on a copy** of production data first
3. **Backup database** before running migrations in production
4. **Use transactions** - migrations should be atomic
5. **Never edit applied migrations** - create a new one instead
6. **Version control migrations** - commit them to Git
7. **Document complex migrations** - add comments explaining why

## NEXT STEPS

Once you've completed this exercise:
- You understand how to evolve database schemas safely
- You can add/modify columns without losing data
- You know how to rollback bad migrations
- You're ready for production database management!

Move on to **Exercise 5: Query Optimization & Audit Logging**
