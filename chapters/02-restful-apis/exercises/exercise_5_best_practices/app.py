"""
Exercise 5: RESTful Best Practices - API Refactoring Challenge - SOLUTION

OBJECTIVE:
Refactor a poorly designed API to follow REST principles and industry best practices.

WHAT YOU'LL LEARN:
- REST conventions and anti-patterns
- URL design principles (resource-based, not action-based)
- Proper HTTP method usage
- Response consistency
- When to use different HTTP methods

CHALLENGE:
Below you'll find a POORLY DESIGNED API with many anti-patterns.
Your job is to refactor it following REST principles.

BAD API ENDPOINTS (provided as reference):
❌ GET    /getAllUsers
❌ POST   /createUser
❌ GET    /getUserById?id=123
❌ POST   /updateUserInfo
❌ POST   /deleteUser?userId=123
❌ GET    /user_search?name=john
❌ POST   /user_activate
❌ POST   /user_deactivate
❌ GET    /fetchUserOrders?userId=123
❌ POST   /placeNewOrder
❌ GET    /getOrderStatus?orderId=456
❌ POST   /cancelOrderNow
❌ GET    /calculate_total?orderId=456

TODO CHECKLIST:
[ ] Identify resources (Users, Orders, etc.)
[ ] Design RESTful URLs (nouns, not verbs)
[ ] Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
[ ] Implement consistent response formats
[ ] Apply proper nesting where appropriate
[ ] Remove redundant endpoints
[ ] Include calculated fields in responses
[ ] Test in Swagger UI

REST PRINCIPLES TO APPLY:
1. Resource-Based URLs: Use nouns (/users), not verbs (/getUsers)
2. HTTP Methods Define Actions: GET reads, POST creates, PUT/PATCH updates, DELETE removes
3. Proper Nesting: /users/{id}/orders for related resources
4. Idempotent Operations: DELETE should use DELETE method, not POST
5. Calculated Fields: Include in response, don't make separate endpoints
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from datetime import datetime

def create_app():
    """
    Create the refactored RESTful API.

    This API demonstrates proper REST design after refactoring.
    """
    app = Flask(__name__)
    CORS(app)

    api = Api(
        app,
        version='5.0',
        title='Refactored RESTful API',
        description='Exercise 5: Apply RESTful Best Practices',
        doc='/swagger'
    )

    # ============================================================================
    # DATA MODELS
    # ============================================================================

    users_ns = Namespace('users', description='User operations')

    user_model = users_ns.model('User', {
        'id': fields.Integer(readonly=True, description='User ID'),
        'name': fields.String(required=True, description='User name'),
        'email': fields.String(required=True, description='User email'),
        'active': fields.Boolean(description='User active status'),
        'created_at': fields.String(description='Account creation date')
    })

    orders_ns = Namespace('orders', description='Order operations')

    order_item_model = orders_ns.model('OrderItem', {
        'product_name': fields.String(required=True),
        'quantity': fields.Integer(required=True),
        'price': fields.Float(required=True)
    })

    order_model = orders_ns.model('Order', {
        'id': fields.Integer(readonly=True, description='Order ID'),
        'user_id': fields.Integer(required=True, description='User ID'),
        'items': fields.List(fields.Nested(order_item_model), required=True),
        'status': fields.String(description='Order status'),
        'total': fields.Float(readonly=True, description='Calculated total'),  # Calculated field!
        'created_at': fields.String(description='Order creation date')
    })

    # ============================================================================
    # IN-MEMORY DATA STORAGE
    # ============================================================================

    users = [
        {
            'id': 1,
            'name': 'John Doe',
            'email': 'john@example.com',
            'active': True,
            'created_at': '2024-01-15'
        },
        {
            'id': 2,
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'active': True,
            'created_at': '2024-02-01'
        }
    ]

    orders = [
        {
            'id': 1,
            'user_id': 1,
            'items': [
                {'product_name': 'Laptop', 'quantity': 1, 'price': 999.99}
            ],
            'status': 'completed',
            'created_at': '2024-03-01'
        }
    ]

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================

    def find_user_by_id(user_id):
        """Find user by ID."""
        for user in users:
            if user['id'] == user_id:
                return user
        return None

    def find_order_by_id(order_id):
        """Find order by ID."""
        for order in orders:
            if order['id'] == order_id:
                return order
        return None

    def calculate_order_total(items):
        """
        Calculate total for an order.

        KEY CONCEPT: Calculated fields should be included in responses,
        not exposed as separate endpoints like /calculate_total
        """
        total = sum(item['price'] * item['quantity'] for item in items)
        return round(total, 2)

    def get_orders_for_user(user_id):
        """Get all orders for a user."""
        return [order for order in orders if order['user_id'] == user_id]

    # ============================================================================
    # USERS ENDPOINTS - RESTful Design
    # ============================================================================

    @users_ns.route('/')
    class UserList(Resource):
        """
        Users collection endpoint.

        REFACTORED FROM:
        ❌ GET /getAllUsers
        ✅ GET /users
        """

        @users_ns.doc('list_users')
        @users_ns.marshal_list_with(user_model)
        def get(self):
            """
            List all users.

            REFACTORING: Changed from /getAllUsers to /users
            WHY: URLs should be resource-based (nouns), not action-based (verbs)

            OLD: GET /getAllUsers
            NEW: GET /users
            """
            return users

        @users_ns.doc('create_user')
        @users_ns.expect(user_model)
        @users_ns.marshal_with(user_model, code=201)
        def post(self):
            """
            Create a new user.

            REFACTORING: Changed from /createUser to /users with POST method

            OLD: POST /createUser
            NEW: POST /users

            WHY: HTTP methods define the action, not the URL
            """
            data = request.json

            # Validate required fields
            if 'name' not in data or 'email' not in data:
                return {'error': 'Missing required fields: name and email'}, 400

            # Generate new ID
            new_id = max([u['id'] for u in users], default=0) + 1

            # Create user
            user = {
                'id': new_id,
                'name': data['name'],
                'email': data['email'],
                'active': True,  # Default to True
                'created_at': datetime.utcnow().strftime('%Y-%m-%d')
            }

            users.append(user)
            return user, 201

    @users_ns.route('/<int:id>')
    @users_ns.param('id', 'User identifier')
    class UserItem(Resource):
        """
        Single user endpoint.

        REFACTORED FROM:
        ❌ GET /getUserById?id=123
        ✅ GET /users/123
        """

        @users_ns.doc('get_user')
        @users_ns.marshal_with(user_model)
        def get(self, id):
            """
            Get user by ID.

            REFACTORING: Changed from query parameter to path parameter

            OLD: GET /getUserById?id=123
            NEW: GET /users/123

            WHY: Resource identifiers belong in the path, not query string
            """
            user = find_user_by_id(id)
            if not user:
                return {'error': 'User not found'}, 404
            return user

        @users_ns.doc('update_user')
        @users_ns.expect(user_model)
        @users_ns.marshal_with(user_model)
        def put(self, id):
            """
            Update user information.

            REFACTORING: Changed from POST to PUT method

            OLD: POST /updateUserInfo
            NEW: PUT /users/{id}

            WHY: PUT is the standard HTTP method for updates
            """
            user = find_user_by_id(id)
            if not user:
                return {'error': 'User not found'}, 404

            data = request.json

            # Update fields
            if 'name' in data:
                user['name'] = data['name']
            if 'email' in data:
                user['email'] = data['email']
            if 'active' in data:
                user['active'] = data['active']

            return user

        @users_ns.doc('delete_user')
        @users_ns.response(204, 'User deleted')
        def delete(self, id):
            """
            Delete a user.

            REFACTORING: Changed from POST with query param to DELETE method

            OLD: POST /deleteUser?userId=123
            NEW: DELETE /users/123

            WHY: DELETE is the idempotent method for removing resources
            """
            user = find_user_by_id(id)
            if not user:
                return {'error': 'User not found'}, 404

            users.remove(user)
            return '', 204

    @users_ns.route('/search')
    class UserSearch(Resource):
        """
        User search endpoint.

        REFACTORED FROM:
        ❌ GET /user_search?name=john
        ✅ GET /users/search?name=john
        """

        @users_ns.doc('search_users', params={'name': 'Search by name (partial match)'})
        @users_ns.marshal_list_with(user_model)
        def get(self):
            """
            Search users by name.

            REFACTORING: Moved under /users resource

            OLD: GET /user_search?name=john
            NEW: GET /users/search?name=john

            WHY: Search is an operation on users, should be under /users
            ALTERNATIVE: Could also use GET /users?name=john (filtering)
            """
            name = request.args.get('name', '')
            if not name:
                return users

            # Filter users where name contains the search term (case-insensitive)
            result = [u for u in users if name.lower() in u['name'].lower()]
            return result

    @users_ns.route('/<int:id>/activate')
    @users_ns.param('id', 'User identifier')
    class UserActivate(Resource):
        """
        User activation endpoint.

        REFACTORED FROM:
        ❌ POST /user_activate (with user_id in body)
        ✅ PATCH /users/{id}/activate
        """

        @users_ns.doc('activate_user')
        @users_ns.marshal_with(user_model)
        def patch(self, id):
            """
            Activate a user account.

            REFACTORING: Changed to PATCH on specific resource

            OLD: POST /user_activate
            NEW: PATCH /users/{id}/activate

            WHY: This is a partial update (changing active field), use PATCH
            WHY: Resource ID should be in path, not body
            """
            user = find_user_by_id(id)
            if not user:
                return {'error': 'User not found'}, 404

            user['active'] = True
            return user

    @users_ns.route('/<int:id>/deactivate')
    @users_ns.param('id', 'User identifier')
    class UserDeactivate(Resource):
        """
        User deactivation endpoint.

        REFACTORED FROM:
        ❌ POST /user_deactivate
        ✅ PATCH /users/{id}/deactivate
        """

        @users_ns.doc('deactivate_user')
        @users_ns.marshal_with(user_model)
        def patch(self, id):
            """
            Deactivate a user account.
            """
            user = find_user_by_id(id)
            if not user:
                return {'error': 'User not found'}, 404

            user['active'] = False
            return user

    @users_ns.route('/<int:id>/orders')
    @users_ns.param('id', 'User identifier')
    class UserOrders(Resource):
        """
        User orders (nested resource).

        REFACTORED FROM:
        ❌ GET /fetchUserOrders?userId=123
        ✅ GET /users/{id}/orders
        """

        @users_ns.doc('get_user_orders')
        @users_ns.marshal_list_with(order_model)
        def get(self, id):
            """
            Get all orders for a user.

            REFACTORING: Changed to nested resource

            OLD: GET /fetchUserOrders?userId=123
            NEW: GET /users/123/orders

            WHY: Orders belong to users, nesting shows this relationship clearly
            WHY: No action verbs like "fetch" in URL
            """
            # Verify user exists
            user = find_user_by_id(id)
            if not user:
                return {'error': 'User not found'}, 404

            # Get all orders for this user
            user_orders = get_orders_for_user(id)

            # Calculate and include total for each order
            for order in user_orders:
                order['total'] = calculate_order_total(order['items'])

            return user_orders

    # ============================================================================
    # ORDERS ENDPOINTS - RESTful Design
    # ============================================================================

    @orders_ns.route('/')
    class OrderList(Resource):
        """
        Orders collection.

        REFACTORED FROM:
        ❌ POST /placeNewOrder
        ✅ POST /orders
        """

        @orders_ns.doc('list_orders')
        @orders_ns.marshal_list_with(order_model)
        def get(self):
            """
            List all orders.
            """
            # Include calculated total for each order
            result = []
            for order in orders:
                order_copy = order.copy()
                order_copy['total'] = calculate_order_total(order['items'])
                result.append(order_copy)
            return result

        @orders_ns.doc('create_order')
        @orders_ns.expect(order_model)
        @orders_ns.marshal_with(order_model, code=201)
        def post(self):
            """
            Create a new order.

            REFACTORING: Changed from action-based to resource-based

            OLD: POST /placeNewOrder
            NEW: POST /orders

            WHY: POST on a collection creates a new resource
            WHY: No need for action verbs like "place" or "new"
            """
            data = request.json

            # Validate required fields
            if 'user_id' not in data or 'items' not in data:
                return {'error': 'Missing required fields: user_id and items'}, 400

            # Verify user exists
            user = find_user_by_id(data['user_id'])
            if not user:
                return {'error': 'User not found'}, 404

            # Validate items list not empty
            if not data['items'] or len(data['items']) == 0:
                return {'error': 'Items list cannot be empty'}, 400

            # Generate new ID
            new_id = max([o['id'] for o in orders], default=0) + 1

            # Create order
            order = {
                'id': new_id,
                'user_id': data['user_id'],
                'items': data['items'],
                'status': 'pending',
                'created_at': datetime.utcnow().strftime('%Y-%m-%d')
            }

            # Calculate and include total
            order['total'] = calculate_order_total(order['items'])

            orders.append(order)
            return order, 201

    @orders_ns.route('/<int:id>')
    @orders_ns.param('id', 'Order identifier')
    class OrderItem(Resource):
        """
        Single order endpoint.

        REFACTORED FROM:
        ❌ GET /getOrderStatus?orderId=456
        ❌ GET /calculate_total?orderId=456
        ✅ GET /orders/456
        """

        @orders_ns.doc('get_order')
        @orders_ns.marshal_with(order_model)
        def get(self, id):
            """
            Get order details including status and total.

            REFACTORING: Consolidated multiple endpoints into one

            OLD: GET /getOrderStatus?orderId=456
            OLD: GET /calculate_total?orderId=456
            NEW: GET /orders/456 (includes both status and total)

            WHY: One resource = one endpoint
            WHY: Calculated values should be included in response,
                 not exposed as separate endpoints
            """
            order = find_order_by_id(id)
            if not order:
                return {'error': 'Order not found'}, 404

            # Include calculated total
            order_copy = order.copy()
            order_copy['total'] = calculate_order_total(order['items'])
            return order_copy

    @orders_ns.route('/<int:id>/cancel')
    @orders_ns.param('id', 'Order identifier')
    class OrderCancel(Resource):
        """
        Cancel order endpoint.

        REFACTORED FROM:
        ❌ POST /cancelOrderNow
        ✅ PATCH /orders/{id}/cancel
        """

        @orders_ns.doc('cancel_order')
        @orders_ns.marshal_with(order_model)
        def patch(self, id):
            """
            Cancel an order.

            REFACTORING: Changed to PATCH on specific resource

            OLD: POST /cancelOrderNow
            NEW: PATCH /orders/{id}/cancel

            WHY: Cancellation is a partial update (changing status)
            WHY: Use PATCH for partial updates
            WHY: Resource ID in path, not body
            """
            order = find_order_by_id(id)
            if not order:
                return {'error': 'Order not found'}, 404

            # Check if already cancelled
            if order['status'] == 'cancelled':
                return {'error': 'Order is already cancelled'}, 400

            # Set status to cancelled
            order['status'] = 'cancelled'

            # Calculate and include total in response
            order_copy = order.copy()
            order_copy['total'] = calculate_order_total(order['items'])
            return order_copy

    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(users_ns, path='/users')
    api.add_namespace(orders_ns, path='/orders')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*80)
    print("REFACTORED RESTful API - Exercise 5: Best Practices")
    print("="*80)
    print("📚 Learning Objectives:")
    print("  - Apply REST principles to API design")
    print("  - Use resource-based URLs (nouns, not verbs)")
    print("  - Use proper HTTP methods")
    print("  - Consolidate redundant endpoints")
    print("\n❌ BAD API DESIGN → ✅ GOOD API DESIGN:")
    print("  ❌ GET /getAllUsers           → ✅ GET /users")
    print("  ❌ POST /createUser           → ✅ POST /users")
    print("  ❌ GET /getUserById?id=123    → ✅ GET /users/123")
    print("  ❌ POST /updateUserInfo       → ✅ PUT /users/{id}")
    print("  ❌ POST /deleteUser?id=123    → ✅ DELETE /users/123")
    print("  ❌ GET /user_search?name=x    → ✅ GET /users/search?name=x")
    print("  ❌ POST /user_activate        → ✅ PATCH /users/{id}/activate")
    print("  ❌ GET /fetchUserOrders?id=1  → ✅ GET /users/1/orders")
    print("  ❌ POST /placeNewOrder        → ✅ POST /orders")
    print("  ❌ GET /getOrderStatus?id=1   → ✅ GET /orders/1")
    print("  ❌ GET /calculate_total?id=1  → ✅ Included in GET /orders/1")
    print("  ❌ POST /cancelOrderNow       → ✅ PATCH /orders/{id}/cancel")
    print("\n💡 REST Principles Applied:")
    print("  1. Resource-based URLs (nouns: /users, /orders)")
    print("  2. HTTP methods define actions (GET, POST, PUT, PATCH, DELETE)")
    print("  3. IDs in path, not query string (/users/123, not ?id=123)")
    print("  4. Nested resources for relationships (/users/1/orders)")
    print("  5. Calculated fields in responses (total included in order)")
    print("  6. One resource = one endpoint (no separate /calculate_total)")
    print("\n🎯 Your Task:")
    print("  - Implement all TODO sections")
    print("  - Notice how the new design is cleaner and more predictable")
    print("  - Compare old vs new endpoint structure")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*80 + "\n")

    app.run(debug=True, port=5000)
