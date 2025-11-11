"""Exercise 2: Login & JWT Token Generation
TODO: Implement login endpoint with JWT tokens
See Exercise 1 for User model - copy it here or import
Your task: Create POST /auth/login that verifies password and returns JWT tokens
"""
from flask import Flask, request
from flask_restx import Api, Namespace, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token
from datetime import timedelta
import os, bcrypt
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app, title='Exercise 2: Login', doc='/swagger')
auth_ns = Namespace('auth')

# TODO 1: Copy User model from Exercise 1 (with set_password and check_password methods)

# TODO 2: Create login model for Swagger
# login_model = auth_ns.model('Login', {...})

# TODO 3: Create Login endpoint
# @auth_ns.route('/login')
# class Login(Resource):
#     def post(self):
#         # 1. Get email and password from request
#         # 2. Find user by email
#         # 3. Verify password with user.check_password()
#         # 4. If invalid: return 401
#         # 5. Create access_token and refresh_token
#         # 6. Return tokens with expires_in

api.add_namespace(auth_ns, path='/auth')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("Exercise 2: Login & JWT Tokens")
    app.run(debug=True, port=5000)
