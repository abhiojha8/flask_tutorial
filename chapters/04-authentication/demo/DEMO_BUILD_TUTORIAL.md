# Building the Authentication Demo - Step-by-Step Tutorial

This tutorial shows the progressive steps to build the authentication demo app.
Use these as teaching checkpoints during live coding.

---

## STEP 1: Project Setup & Database Connection

**What we're building:** Basic Flask app connected to database

```
PROJECT STRUCTURE:
auth_demo/
  ├── app.py
  ├── .env
  ├── .env.example
  └── requirements.txt

INSTALL:
pip install flask flask-restx flask-sqlalchemy flask-jwt-extended
pip install bcrypt python-dotenv flask-cors psycopg2-binary

.env FILE:
DATABASE_URL="postgresql://..."
JWT_SECRET_KEY="your-secret-key"
```

**Code checkpoint:**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()
    print("Database connected!")

if __name__ == '__main__':
    app.run(debug=True)
```

**Test:** Run and see "Database connected!"

---

## STEP 2: User Model with Password Hashing

**What we're adding:** User table with secure password storage

```
USER MODEL:
- id (primary key)
- username (unique)
- email (unique)
- password_hash (NOT plain password!)
- role (reader/author/admin)
- is_active
- created_at, updated_at
```

**Code:**
```python
import bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users_auth'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='reader', index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hash password with bcrypt"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }
```

**Test in Python shell:**
```python
user = User(username='test', email='test@example.com')
user.set_password('SecurePass123')
print(user.password_hash)  # Shows hash
user.check_password('SecurePass123')  # True
```

---

## STEP 3: Flask-RESTX API Setup

**What we're adding:** Swagger UI and API structure

```python
from flask_restx import Api, Namespace

api = Api(
    app,
    title='Secure Blog API',
    description='Authentication demo',
    doc='/swagger'
)

auth_ns = Namespace('auth', description='Authentication')
api.add_namespace(auth_ns, path='/auth')
```

**Test:** Open http://localhost:5000/swagger

---

## STEP 4: Registration Endpoint

**What we're adding:** User can create account

```python
from flask import request
from flask_restx import Resource, fields
import re

# Define input model
register_model = auth_ns.model('Register', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'role': fields.String(enum=['reader', 'author', 'admin'], default='reader')
})

def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    def post(self):
        data = request.json

        # Validate email
        if not validate_email(data['email']):
            return {'error': 'Invalid email'}, 400

        # Check duplicates
        if User.query.filter_by(username=data['username']).first():
            return {'error': 'Username exists'}, 409

        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email exists'}, 409

        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'reader')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return user.to_dict(), 201
```

**Test in Swagger:**
- POST /auth/register with valid data → 201
- Try same email → 409 Conflict

---

## STEP 5: JWT Configuration

**What we're adding:** JWT token management

```python
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from datetime import timedelta

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

jwt = JWTManager(app)
```

---

## STEP 6: Login Endpoint

**What we're adding:** User can login and get JWT

```python
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json

        # Find user
        user = User.query.filter_by(email=data['email']).first()

        # Verify password
        if not user or not user.check_password(data['password']):
            return {'error': 'Invalid credentials'}, 401

        # Check if active
        if not user.is_active:
            return {'error': 'Account disabled'}, 403

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }, 200
```

**Test:**
- POST /auth/login with correct credentials → Get tokens
- POST /auth/login with wrong password → 401

---

## STEP 7: Protected Endpoint (Current User)

**What we're adding:** Get user info from token

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@auth_ns.route('/me')
class CurrentUser(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {'error': 'User not found'}, 404

        return user.to_dict(), 200
```

**Test:**
- GET /auth/me without token → 401
- Click "Authorize", enter "Bearer <token>"
- GET /auth/me → Returns user info

---

## STEP 8: Post Model & Relationships

**What we're adding:** Posts belonging to users

```python
class Post(db.Model):
    __tablename__ = 'posts_auth'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users_auth.id'))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'is_published': self.is_published,
            'author_id': self.author_id
        }

# Add to User model
User.posts = db.relationship('Post', backref='author', cascade='all, delete-orphan')
```

---

## STEP 9: Role-Based Access Control

**What we're adding:** Custom decorator for roles

```python
from functools import wraps

def require_role(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or user.role not in allowed_roles:
                return {'error': f'Requires {allowed_roles} role'}, 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Use it
posts_ns = Namespace('posts', description='Blog posts')

@posts_ns.route('/')
class PostList(Resource):
    @require_role('author', 'admin')
    def post(self):
        user_id = get_jwt_identity()

        post = Post(
            author_id=user_id,
            title=request.json['title'],
            content=request.json['content']
        )

        db.session.add(post)
        db.session.commit()

        return post.to_dict(), 201
```

**Test:**
- Register as "reader" → Login
- Try POST /posts → 403 Forbidden
- Register as "author" → Login
- POST /posts → Success!

---

## STEP 10: Token Refresh

**What we're adding:** Get new access token

```python
@auth_ns.route('/refresh')
class RefreshToken(Resource):
    @jwt_required(refresh=True)  # Uses refresh token!
    def post(self):
        user_id = get_jwt_identity()
        new_token = create_access_token(identity=user_id)

        return {
            'access_token': new_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }, 200
```

**Test:**
- Wait for access token to expire (or set short expiry for testing)
- Use protected endpoint → 401 Expired
- POST /auth/refresh with refresh token → Get new access token
- Use new token → Success!

---

## STEP 11: Token Blacklist (Logout)

**What we're adding:** Revoke tokens on logout

```python
from flask_jwt_extended import get_jwt

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist_auth'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def is_blacklisted(jti):
        return TokenBlacklist.query.filter_by(jti=jti).first() is not None

# JWT callback
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return TokenBlacklist.is_blacklisted(jwt_payload['jti'])

@auth_ns.route('/logout')
class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']

        blacklist = TokenBlacklist(jti=jti)
        db.session.add(blacklist)
        db.session.commit()

        return {'message': 'Logged out'}, 200
```

**Test:**
- POST /auth/logout → 200
- Try using same token → 401 Revoked

---

## STEP 12: Admin Endpoints

**What we're adding:** Admin-only user management

```python
admin_ns = Namespace('admin', description='Admin operations')

@admin_ns.route('/users')
class AdminUserList(Resource):
    @require_role('admin')
    def get(self):
        users = User.query.all()
        return [user.to_dict() for user in users], 200

@admin_ns.route('/users/<int:user_id>')
class AdminUserItem(Resource):
    @require_role('admin')
    def delete(self, user_id):
        current_user_id = get_jwt_identity()

        if current_user_id == user_id:
            return {'error': 'Cannot delete yourself'}, 400

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return '', 204

api.add_namespace(admin_ns, path='/admin')
```

**Test:**
- Login as "reader" → Try GET /admin/users → 403
- Login as "admin" → GET /admin/users → Success!

---

## Complete Flow Testing

1. **Register** → POST /auth/register
2. **Login** → POST /auth/login → Get tokens
3. **View Profile** → GET /auth/me (with token)
4. **Create Post** → POST /posts (needs author role)
5. **Refresh Token** → POST /auth/refresh
6. **Logout** → POST /auth/logout
7. **Try Using Token** → 401 Revoked

---

## Security Checklist

✅ Passwords hashed with bcrypt
✅ JWT tokens signed with secret key
✅ Access tokens short-lived (1 hour)
✅ Refresh tokens for convenience
✅ Token blacklist for logout
✅ Role-based access control
✅ Email validation
✅ Duplicate checking
✅ Environment variables for secrets

---

## Next Steps

- Add password strength requirements
- Implement password reset flow
- Add email verification
- Implement rate limiting
- Add two-factor authentication (2FA)
- Add API key authentication for services

---

**Production Tips:**
- Use HTTPS (tokens can be intercepted on HTTP!)
- Rotate JWT_SECRET_KEY periodically
- Set secure cookie flags if using cookies
- Implement brute-force protection
- Log authentication attempts
- Monitor for suspicious activity
