"""Exercise 3: Protected Routes with JWT
TODO: Implement @jwt_required to protect endpoints
Create GET /auth/me to get current user from token
"""
from flask import Flask, request
from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app, title='Exercise 3: Protected Routes', doc='/swagger',
          authorizations={'Bearer': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}},
          security='Bearer')
auth_ns = Namespace('auth')

# TODO 1: Copy User model from previous exercises

# TODO 2: Create GET /auth/me endpoint
# @auth_ns.route('/me')
# class CurrentUser(Resource):
#     @jwt_required()  # This decorator protects the endpoint!
#     def get(self):
#         # 1. Get user_id from token: user_id = get_jwt_identity()
#         # 2. Query user from database
#         # 3. Return user.to_dict()

# TODO 3: Create PUT /auth/me to update profile
#     def put(self):
#         # Allow user to update username/email
#         # Check for duplicates
#         # Update and return

api.add_namespace(auth_ns, path='/auth')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("Exercise 3: Protected Routes")
    print("Use 'Authorize' button in Swagger to add token")
    app.run(debug=True, port=5000)
