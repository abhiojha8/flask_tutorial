"""Exercise 5: Token Refresh & Logout
TODO: Implement refresh token endpoint and token blacklisting
"""
from flask import Flask, request
from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt, create_access_token
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app, title='Exercise 5: Refresh & Logout', doc='/swagger',
          authorizations={'Bearer': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}},
          security='Bearer')
auth_ns = Namespace('auth')

# TODO 1: Create TokenBlacklist model
# class TokenBlacklist(db.Model):
#     __tablename__ = 'token_blacklist_ex5'
#     id, jti, created_at
#     @staticmethod
#     def is_blacklisted(jti): ...

# TODO 2: Register JWT callback
# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     return TokenBlacklist.is_blacklisted(jwt_payload['jti'])

# TODO 3: Create refresh endpoint
# @auth_ns.route('/refresh')
# class RefreshToken(Resource):
#     @jwt_required(refresh=True)  # Needs REFRESH token!
#     def post(self):
#         # Get user_id and create new access token
#         pass

# TODO 4: Create logout endpoint
# @auth_ns.route('/logout')
# class Logout(Resource):
#     @jwt_required()
#     def post(self):
#         # Get jti from current token
#         # Add to blacklist
#         # Return success message

api.add_namespace(auth_ns, path='/auth')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("Exercise 5: Token Refresh & Logout")
    print("Test: Login -> Logout -> Try using same token (should fail)")
    app.run(debug=True, port=5000)
