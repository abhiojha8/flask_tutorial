"""Exercise 4: Role-Based Access Control
TODO: Implement custom @require_role decorator
Create endpoints that check user roles before allowing access
"""
from flask import Flask, request
from flask_restx import Api, Namespace, Resource
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db = SQLAlchemy(app)
jwt = JWTManager(app)
api = Api(app, title='Exercise 4: RBAC', doc='/swagger',
          authorizations={'Bearer': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}},
          security='Bearer')

# TODO 1: Copy User and Post models (User should have 'role' field)

# TODO 2: Create custom decorator
# def require_role(*allowed_roles):
#     def decorator(fn):
#         @wraps(fn)
#         @jwt_required()
#         def wrapper(*args, **kwargs):
#             # 1. Get user_id from token
#             # 2. Get user from database
#             # 3. Check if user.role in allowed_roles
#             # 4. If not: return 403 Forbidden
#             # 5. If yes: call fn(*args, **kwargs)
#         return wrapper
#     return decorator

# TODO 3: Create posts endpoint with role checking
# posts_ns = Namespace('posts')
# @posts_ns.route('/')
# class PostList(Resource):
#     @require_role('author', 'admin')  # Only authors and admins!
#     def post(self):
#         # Create post for authenticated user
#         pass

api.add_namespace(Namespace('auth'), path='/auth')  # Add your auth endpoints
# api.add_namespace(posts_ns, path='/posts')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("Exercise 4: Role-Based Access Control")
    print("Register as 'reader' - try creating post (should fail)")
    print("Register as 'author' - try creating post (should work)")
    app.run(debug=True, port=5000)
