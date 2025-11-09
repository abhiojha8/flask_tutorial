"""
Exercise 4: Database Migrations with Alembic

OBJECTIVE:
Learn to manage database schema changes using migrations instead of
dropping and recreating tables (which loses data!).

This file provides the base models. You'll modify them and use Alembic
to generate migrations for the changes.

IMPORTANT:
This exercise is different from the others. Instead of filling in TODOs
in this file, you'll be:
1. Setting up Alembic
2. Creating migrations from the command line
3. Modifying models in this file
4. Generating new migrations for those changes

See README.md for detailed instructions!
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL not found!")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# ============================================================================
# BASE MODELS
# ============================================================================
# These are the models you'll start with.
# You'll modify them as part of the exercise to learn about migrations.

class Organization(db.Model):
    """Organization model (from Exercise 3)."""
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    plan = db.Column(db.String(20), default='free')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='organization', lazy=True)
    posts = db.relationship('Post', backref='organization', lazy=True)


class User(db.Model):
    """
    User model (from Exercise 3).

    NEW (in Part 3): Added bio and avatar_url columns via migration:
    - bio: db.Column(db.Text, nullable=True)
    - avatar_url: db.Column(db.String(255), nullable=True)
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')


class Post(db.Model):
    """
    Post model (from Exercise 3).

    NEW (in Part 4): Added category_id column via migration:
    - category_id: db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='draft')
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# NEW (in Part 4): Category model added
class Category(db.Model):
    """Category model for organizing posts."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to posts
    posts = db.relationship('Post', backref='category', lazy=True)


if __name__ == '__main__':
    print("="*70)
    print("EXERCISE 4: DATABASE MIGRATIONS WITH ALEMBIC")
    print("="*70)
    print("\n⚠️  DON'T RUN THIS FILE DIRECTLY!")
    print("\nThis exercise uses Alembic CLI commands, not the Flask app.")
    print("\n📚 Follow the instructions in README.md:")
    print("   1. Initialize Alembic")
    print("   2. Configure alembic.ini and env.py")
    print("   3. Create initial migration")
    print("   4. Modify models and generate new migrations")
    print("   5. Apply migrations with 'alembic upgrade head'")
    print("\n💡 Key Learning:")
    print("   Migrations let you evolve your database schema")
    print("   WITHOUT losing existing data!")
    print("\n" + "="*70 + "\n")
