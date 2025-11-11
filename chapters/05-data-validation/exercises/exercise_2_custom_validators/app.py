"""
Exercise 2: Custom Validators
Chapter 5: Data Validation & Error Handling

Learning Objectives:
- Create custom validation functions
- Use @validates decorator for field validation
- Implement password strength checking
- Build reusable validators

TODO: Complete the marked sections to implement custom validators!
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from marshmallow import Schema, fields as ma_fields, validates, ValidationError, EXCLUDE
from marshmallow.validate import Length, Email as EmailValidator
from datetime import datetime
import os
import re
from dotenv import load_dotenv
import bcrypt

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api = Api(
    app,
    version='1.0',
    title='Exercise 2: Custom Validators',
    description='Learn to create custom validation logic for business rules',
    doc='/swagger'
)

# ============================================================================
# DATABASE MODEL
# ============================================================================

class User(db.Model):
    __tablename__ = 'users_ex2'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone
        }

# ============================================================================
# TODO 1: Create Password Strength Validator Function
# ============================================================================
# Create a function that validates password strength with these rules:
# - At least 8 characters long
# - Contains at least one uppercase letter
# - Contains at least one lowercase letter
# - Contains at least one digit
# - Contains at least one special character (!@#$%^&*(),.?":{}|<>)
#
# Hints:
# - Use re.search(r'[A-Z]', password) to check for uppercase
# - Use re.search(r'[a-z]', password) for lowercase
# - Use re.search(r'\d', password) for digits
# - Raise ValidationError('Your message') for each failed check

def validate_password_strength(password):
    """Custom validator for password strength"""

    # TODO: Check minimum length (8 characters)
    # if len(password) < 8:
    #     raise ValidationError('Password must be at least 8 characters')

    # TODO: Check for uppercase letter
    # if not re.search(r'[A-Z]', password):
    #     raise ValidationError('Password must contain at least one uppercase letter')

    # TODO: Check for lowercase letter
    # ...

    # TODO: Check for digit
    # ...

    # TODO: Check for special character
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     raise ValidationError('Password must contain at least one special character')

    pass  # Remove this when you implement the function

# ============================================================================
# TODO 2: Create Username Blacklist Validator
# ============================================================================
# Create a function that prevents reserved usernames
# Reserved list: ['admin', 'root', 'system', 'moderator', 'administrator']
#
# Hints:
# - Check if username.lower() is in the reserved list
# - Raise ValidationError if it's reserved

def validate_username_not_reserved(username):
    """Prevent reserved usernames"""

    # TODO: Define reserved usernames list
    # reserved = ['admin', 'root', 'system', 'moderator', 'administrator']

    # TODO: Check if username (lowercase) is in reserved list
    # if username.lower() in reserved:
    #     raise ValidationError(f'Username "{username}" is reserved')

    pass

# ============================================================================
# TODO 3: Create Email Domain Validator
# ============================================================================
# Create a function that blocks temporary email domains
# Blocked domains: ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
#
# Hints:
# - Extract domain with email.split('@')[1]
# - Check if domain is in blocked list

def validate_email_domain(email):
    """Block temporary email providers"""

    # TODO: Define blocked domains
    # blocked_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']

    # TODO: Extract domain from email
    # domain = email.split('@')[1]

    # TODO: Check if domain is blocked
    # if domain in blocked_domains:
    #     raise ValidationError('Temporary email addresses are not allowed')

    pass

# ============================================================================
# TODO 4: Create Phone Number Validator
# ============================================================================
# Validate US phone number format:
# - Accepts: (123) 456-7890, 123-456-7890, 1234567890, +1 (123) 456-7890
#
# Hints:
# - Use regex pattern: r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
# - Use re.match(pattern, phone)

def validate_phone_format(phone):
    """Validate phone number format"""

    # TODO: Define regex pattern for US phone
    # pattern = r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'

    # TODO: Check if phone matches pattern
    # if not re.match(pattern, phone):
    #     raise ValidationError('Invalid phone format. Use: (123) 456-7890 or 123-456-7890')

    pass

# ============================================================================
# TODO 5: Create UserSchema with Custom Validators
# ============================================================================

class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = ma_fields.Str(
        required=True,
        validate=Length(min=3, max=50)
    )
    email = ma_fields.Email(required=True)
    password = ma_fields.Str(required=True)
    phone = ma_fields.Str(required=False, allow_none=True)

    # TODO: Add @validates('username') decorator to validate username
    # Use the validate_username_not_reserved function
    # @validates('username')
    # def validate_username(self, value):
    #     # Check if starts with letter
    #     if not value[0].isalpha():
    #         raise ValidationError('Username must start with a letter')
    #
    #     # Check for reserved names
    #     validate_username_not_reserved(value)
    #
    #     # Check if already exists
    #     if User.query.filter_by(username=value).first():
    #         raise ValidationError('Username already exists')

    # TODO: Add @validates('email') decorator to validate email domain
    # Use the validate_email_domain function
    # @validates('email')
    # def validate_email(self, value):
    #     validate_email_domain(value)
    #
    #     # Check if exists
    #     if User.query.filter_by(email=value).first():
    #         raise ValidationError('Email already registered')

    # TODO: Add @validates('password') decorator for password strength
    # Use the validate_password_strength function
    # @validates('password')
    # def validate_password(self, value):
    #     validate_password_strength(value)

    # TODO: Add @validates('phone') decorator for phone format
    # Only validate if phone is provided (check if value is not None)
    # @validates('phone')
    # def validate_phone(self, value):
    #     if value:  # Only validate if provided
    #         validate_phone_format(value)

# ============================================================================
# NAMESPACE & MODEL
# ============================================================================

users_ns = Namespace('users', description='User operations')
api.add_namespace(users_ns, path='/users')

user_model = users_ns.model('User', {
    'username': fields.String(required=True, description='Username (3-50 chars, not reserved)'),
    'email': fields.String(required=True, description='Email (not temporary domain)'),
    'password': fields.String(required=True, description='Strong password (8+ chars, upper, lower, digit, special)'),
    'phone': fields.String(description='Phone number (US format)')
})

# ============================================================================
# TODO 6: Implement Registration Endpoint
# ============================================================================

@users_ns.route('/register')
class UserRegister(Resource):
    @users_ns.expect(user_model)
    def post(self):
        """Register user with custom validation"""

        # TODO: Create schema and validate
        # schema = UserSchema()
        #
        # try:
        #     data = schema.load(request.json)
        # except ValidationError as err:
        #     return {'errors': err.messages}, 400

        # TODO: Create user
        # user = User(
        #     username=data['username'],
        #     email=data['email'],
        #     phone=data.get('phone')
        # )
        # user.set_password(data['password'])
        #
        # db.session.add(user)
        # db.session.commit()

        # TODO: Return success
        # return {'message': 'User registered', 'user': user.to_dict()}, 201

        return {'error': 'Not implemented. Complete TODO 6!'}, 501

@users_ns.route('/')
class UserList(Resource):
    def get(self):
        """Get all users"""
        users = User.query.all()
        return {'users': [u.to_dict() for u in users]}, 200

# ============================================================================
# DATABASE INIT
# ============================================================================

with app.app_context():
    db.create_all()
    print("✅ Database table created: users_ex2")

# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔐 EXERCISE 2: Custom Validators")
    print("="*70)
    print("\nTODO List:")
    print("  1. Create validate_password_strength() function")
    print("  2. Create validate_username_not_reserved() function")
    print("  3. Create validate_email_domain() function")
    print("  4. Create validate_phone_format() function")
    print("  5. Add @validates decorators to UserSchema")
    print("  6. Implement registration endpoint with validation")
    print("\nTest Cases:")
    print("  ✓ Password 'weak' → Multiple errors (length, uppercase, digit, special)")
    print("  ✓ Username 'admin' → Reserved username error")
    print("  ✓ Email 'test@tempmail.com' → Temporary email error")
    print("  ✓ Phone '12345' → Invalid format error")
    print("  ✓ Valid data → Success!")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
