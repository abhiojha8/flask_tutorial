"""
Exercise 1: User Registration & Password Hashing

Learning Objectives:
- Implement secure password hashing with bcrypt
- Validate email format
- Check for duplicate users
- Return appropriate status codes

TODO: Complete the marked sections!
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import re
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api = Api(
    app,
    title='Exercise 1: User Registration',
    description='Learn secure password hashing and user registration',
    doc='/swagger'
)

auth_ns = Namespace('auth', description='Authentication operations')

# TODO 1: Create User Model with password hashing
# Create a User model with these fields:
# - id: Integer, primary key
# - username: String(80), unique, nullable=False
# - email: String(120), unique, nullable=False
# - password_hash: String(255), nullable=False
# - created_at: DateTime, default=datetime.utcnow
#
# Add these methods to User:
# - set_password(self, password): Hash password with bcrypt and store in password_hash
#   Hint: bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#
# - check_password(self, password): Verify password
#   Hint: bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
#
# - to_dict(self): Return dictionary with id, username, email, created_at
#   Hint: Don't include password_hash!


# TODO 2: Create validation functions
# def validate_email(email):
#     """Validate email format using regex"""
#     # Return True if email matches pattern: letters@letters.letters
#     # Hint: re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None
#
# def validate_password_strength(password):
#     """Validate password meets requirements"""
#     # Check:
#     # - At least 8 characters
#     # - Contains at least one number
#     # - Contains at least one letter
#     # Return (True, None) if valid
#     # Return (False, error_message) if invalid


# TODO 3: Create Swagger models
# register_model = auth_ns.model('Register', {
#     'username': fields.String(required=True, min_length=3, example='johndoe'),
#     'email': fields.String(required=True, example='john@example.com'),
#     'password': fields.String(required=True, min_length=8, example='SecurePass123')
# })


# TODO 4: Create Registration endpoint
# @auth_ns.route('/register')
# class Register(Resource):
#     @auth_ns.expect(register_model, validate=True)
#     def post(self):
#         """Register a new user"""
#         # 1. Get data from request.json
#         # 2. Validate email format (return 400 if invalid)
#         # 3. Validate password strength (return 400 if weak)
#         # 4. Check if username exists (return 409 if exists)
#         # 5. Check if email exists (return 409 if exists)
#         # 6. Create user, set password (hash it!)
#         # 7. Add to db, commit
#         # 8. Return user.to_dict(), 201


api.add_namespace(auth_ns, path='/auth')

with app.app_context():
    db.create_all()
    print("[OK] Database tables created!")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Exercise 1: User Registration & Password Hashing")
    print("="*60)
    print("Swagger UI: http://localhost:5000/swagger")
    print("\nTODO:")
    print("  1. Create User model with password hashing methods")
    print("  2. Implement email and password validation")
    print("  3. Create registration endpoint with duplicate checking")
    print("  4. Test in Swagger UI")
    print("="*60 + "\n")

    app.run(debug=True, port=5000)
