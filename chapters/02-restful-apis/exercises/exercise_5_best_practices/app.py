"""
Exercise 5: RESTful Best Practices - API Refactoring Challenge

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
        # TODO: Implement this helper
        pass

    def find_order_by_id(order_id):
        """Find order by ID."""
        # TODO: Implement this helper
        pass

    def calculate_order_total(items):
        """
        Calculate total for an order.

        TODO: Implement total calculation
        HINT: sum(item['price'] * item['quantity'] for item in items)
        HINT: Round to 2 decimal places

        KEY CONCEPT: Calculated fields should be included in responses,
        not exposed as separate endpoints like /calculate_total
        """
        # TODO: Implement calculation
        pass

    def get_orders_for_user(user_id):
        """Get all orders for a user."""
        # TODO: Return list of orders where order['user_id'] == user_id
        pass

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

            TODO: Implement this endpoint
            REFACTORING: Changed from /getAllUsers to /users
            WHY: URLs should be resource-based (nouns), not action-based (verbs)

            OLD: GET /getAllUsers
            NEW: GET /users
            """
            # TODO: Return users list
            pass

        @users_ns.doc('create_user')
        @users_ns.expect(user_model)
        @users_ns.marshal_with(user_model, code=201)
        def post(self):
            """
            Create a new user.

            TODO: Implement user creation
            REFACTORING: Changed from /createUser to /users with POST method

            OLD: POST /createUser
            NEW: POST /users

            WHY: HTTP methods define the action, not the URL
            """
            # TODO: Implement POST /users
            # STEPS:
            # 1. Get request data
            # 2. Validate required fields (name, email)
            # 3. Generate new ID
            # 4. Set active to True by default
            # 5. Set created_at to today
            # 6. Add to users list
            # 7. Return user with 201
            pass

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

            TODO: Implement this endpoint
            REFACTORING: Changed from query parameter to path parameter

            OLD: GET /getUserById?id=123
            NEW: GET /users/123

            WHY: Resource identifiers belong in the path, not query string
            """
            # TODO: Find user by ID, return 404 if not found
            pass

        @users_ns.doc('update_user')
        @users_ns.expect(user_model)
        @users_ns.marshal_with(user_model)
        def put(self, id):
            """
            Update user information.

            TODO: Implement user update
            REFACTORING: Changed from POST to PUT method

            OLD: POST /updateUserInfo
            NEW: PUT /users/{id}

            WHY: PUT is the standard HTTP method for updates
            """
            # TODO: Implement PUT /users/{id}
            pass

        @users_ns.doc('delete_user')
        @users_ns.response(204, 'User deleted')
        def delete(self, id):
            """
            Delete a user.

            TODO: Implement user deletion
            REFACTORING: Changed from POST with query param to DELETE method

            OLD: POST /deleteUser?userId=123
            NEW: DELETE /users/123

            WHY: DELETE is the idempotent method for removing resources
            """
            # TODO: Implement DELETE /users/{id}
            pass

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

            TODO: Implement search
            REFACTORING: Moved under /users resource

            OLD: GET /user_search?name=john
            NEW: GET /users/search?name=john

            WHY: Search is an operation on users, should be under /users
            ALTERNATIVE: Could also use GET /users?name=john (filtering)

            HINT: Get 'name' from request.args
            HINT: Filter users where name contains the search term (case-insensitive)
            """
            # TODO: Implement search
            pass

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

            TODO: Implement activation
            REFACTORING: Changed to PATCH on specific resource

            OLD: POST /user_activate
            NEW: PATCH /users/{id}/activate

            WHY: This is a partial update (changing active field), use PATCH
            WHY: Resource ID should be in path, not body

            STEPS:
            1. Find user (404 if not found)
            2. Set active to True
            3. Return updated user with 200
            """
            # TODO: Implement PATCH /users/{id}/activate
            pass

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

            TODO: Implement deactivation
            HINT: Similar to activate, but set active to False
            """
            # TODO: Implement PATCH /users/{id}/deactivate
            pass

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

            TODO: Implement this endpoint
            REFACTORING: Changed to nested resource

            OLD: GET /fetchUserOrders?userId=123
            NEW: GET /users/123/orders

            WHY: Orders belong to users, nesting shows this relationship clearly
            WHY: No action verbs like "fetch" in URL

            STEPS:
            1. Verify user exists (404 if not)
            2. Get all orders for this user
            3. For each order, calculate and include total
            4. Return orders list
            """
            # TODO: Implement GET /users/{id}/orders
            pass

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

            TODO: Implement this endpoint
            HINT: Include calculated total for each order
            """
            # TODO: Return all orders with totals
            pass

        @orders_ns.doc('create_order')
        @orders_ns.expect(order_model)
        @orders_ns.marshal_with(order_model, code=201)
        def post(self):
            """
            Create a new order.

            TODO: Implement order creation
            REFACTORING: Changed from action-based to resource-based

            OLD: POST /placeNewOrder
            NEW: POST /orders

            WHY: POST on a collection creates a new resource
            WHY: No need for action verbs like "place" or "new"

            STEPS:
            1. Get request data
            2. Validate required fields (user_id, items)
            3. Verify user exists
            4. Validate items list not empty
            5. Generate new ID
            6. Set status to 'pending'
            7. Set created_at to today
            8. Calculate and include total
            9. Add to orders list
            10. Return order with 201
            """
            # TODO: Implement POST /orders
            pass

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

            TODO: Implement this endpoint
            REFACTORING: Consolidated multiple endpoints into one

            OLD: GET /getOrderStatus?orderId=456
            OLD: GET /calculate_total?orderId=456
            NEW: GET /orders/456 (includes both status and total)

            WHY: One resource = one endpoint
            WHY: Calculated values should be included in response,
                 not exposed as separate endpoints

            HINT: Include calculated total in response
            """
            # TODO: Find order, calculate total, return with 200
            pass

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

            TODO: Implement order cancellation
            REFACTORING: Changed to PATCH on specific resource

            OLD: POST /cancelOrderNow
            NEW: PATCH /orders/{id}/cancel

            WHY: Cancellation is a partial update (changing status)
            WHY: Use PATCH for partial updates
            WHY: Resource ID in path, not body

            STEPS:
            1. Find order (404 if not found)
            2. Check if already cancelled (400 if already cancelled)
            3. Set status to 'cancelled'
            4. Calculate and include total in response
            5. Return updated order with 200
            """
            # TODO: Implement PATCH /orders/{id}/cancel
            pass

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
