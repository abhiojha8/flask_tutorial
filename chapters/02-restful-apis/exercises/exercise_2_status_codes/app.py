"""
Exercise 2: Status Codes & Error Handling - E-commerce Product Catalog API

OBJECTIVE:
Implement proper HTTP status codes and meaningful error messages for different scenarios.

WHAT YOU'LL BUILD:
- Products resource with comprehensive validation
- Orders resource with business logic validation
- Structured error responses
- Multiple types of validation (input, business rules)

LEARNING GOALS:
- When to use each status code (200, 201, 204, 400, 404, 409, 422)
- Error response formats with helpful messages
- Input validation (format, type, required fields)
- Business rule validation (stock, uniqueness, relationships)
- Field-level error details

STATUS CODES REFERENCE:
200 OK              - Successful GET, PUT, PATCH
201 Created         - Successful POST
204 No Content      - Successful DELETE
400 Bad Request     - Invalid request data (malformed, missing required)
404 Not Found       - Resource doesn't exist
409 Conflict        - Business rule conflict (duplicate, constraint violation)
422 Unprocessable   - Validation failed (invalid values)

TODO CHECKLIST:
[ ] Implement Products endpoints with validation
[ ] Implement Orders endpoints with stock checking
[ ] Use correct status code for each error scenario
[ ] Return structured error responses with details
[ ] Validate all product fields (SKU unique, price > 0, stock >= 0)
[ ] Validate order creation (products exist, stock available)
[ ] Test all error cases in Swagger UI
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from datetime import datetime
import re

def create_app():
    """
    Create the E-commerce Product Catalog API.

    This API demonstrates proper status codes and error handling.
    """
    app = Flask(__name__)
    CORS(app)

    api = Api(
        app,
        version='2.0',
        title='Product Catalog API',
        description='Exercise 2: Master Status Codes and Error Handling',
        doc='/swagger'
    )

    # ============================================================================
    # DATA MODELS
    # ============================================================================

    products_ns = Namespace('products', description='Product operations')

    product_model = products_ns.model('Product', {
        'id': fields.Integer(readonly=True, description='Product ID'),
        'sku': fields.String(required=True, description='Stock Keeping Unit (unique)'),
        'name': fields.String(required=True, description='Product name'),
        'description': fields.String(description='Product description'),
        'price': fields.Float(required=True, description='Product price'),
        'stock_quantity': fields.Integer(required=True, description='Available stock'),
        'category': fields.String(required=True, description='Product category')
    })

    orders_ns = Namespace('orders', description='Order operations')

    order_item_model = orders_ns.model('OrderItem', {
        'product_id': fields.Integer(required=True, description='Product ID'),
        'quantity': fields.Integer(required=True, description='Quantity ordered')
    })

    order_model = orders_ns.model('Order', {
        'id': fields.Integer(readonly=True, description='Order ID'),
        'customer_email': fields.String(required=True, description='Customer email'),
        'items': fields.List(fields.Nested(order_item_model), required=True, description='Order items'),
        'total_amount': fields.Float(required=True, description='Total order amount'),
        'status': fields.String(description='Order status'),
        'created_at': fields.String(description='Order creation timestamp')
    })

    # ============================================================================
    # IN-MEMORY DATA STORAGE
    # ============================================================================

    # Valid categories (for validation)
    VALID_CATEGORIES = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Toys', 'Sports']

    # Products storage
    products = [
        {
            'id': 1,
            'sku': 'LAPTOP-001',
            'name': 'Premium Laptop',
            'description': 'High-performance laptop for professionals',
            'price': 1299.99,
            'stock_quantity': 15,
            'category': 'Electronics'
        },
        {
            'id': 2,
            'sku': 'BOOK-042',
            'name': 'Python Programming Guide',
            'description': 'Comprehensive Python tutorial',
            'price': 49.99,
            'stock_quantity': 100,
            'category': 'Books'
        }
    ]

    # Orders storage
    orders = []

    # ============================================================================
    # ERROR RESPONSE HELPER
    # ============================================================================

    def create_error_response(code, message, details=None, status_code=400):
        """
        Create a standardized error response.

        Args:
            code: Error code (e.g., 'VALIDATION_ERROR', 'NOT_FOUND')
            message: Human-readable error message
            details: Dictionary of field-level errors or additional info
            status_code: HTTP status code to return

        Returns:
            Tuple of (error_dict, status_code)
        """
        # TODO: Implement this helper function
        # HINT: Return a dictionary with structure:
        # {
        #     'error': {
        #         'code': code,
        #         'message': message,
        #         'details': details,
        #         'timestamp': current ISO timestamp,
        #         'path': request.path (use from flask import request)
        #     }
        # }
        # HINT: Return tuple (error_dict, status_code)
        # HINT: Use datetime.utcnow().isoformat() + 'Z' for timestamp
        pass

    # ============================================================================
    # VALIDATION HELPERS
    # ============================================================================

    def validate_email(email):
        """
        Validate email format.

        TODO: Implement email validation
        HINT: Use regex pattern: r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        HINT: Return True if valid, False otherwise
        HINT: Use re.match(pattern, email)
        """
        # TODO: Implement email validation
        pass

    def validate_product_data(data, is_update=False, existing_product=None):
        """
        Validate product data and return detailed errors.

        Args:
            data: Product data to validate
            is_update: Whether this is an update operation
            existing_product: Existing product (for updates)

        Returns:
            Dictionary of field errors, or None if valid

        TODO: Implement comprehensive product validation
        VALIDATION RULES:
        - name: 3-200 characters (422 if invalid)
        - sku: required, unique (409 if duplicate)
        - price: must be > 0 (422 if invalid)
        - stock_quantity: must be >= 0 (422 if invalid)
        - category: must be in VALID_CATEGORIES (422 if invalid)

        HINT: Build errors dict like: {'field_name': 'error message'}
        HINT: For SKU uniqueness, check if any product has same SKU (excluding current product if updating)
        HINT: Return None if no errors, return errors dict if validation fails
        """
        errors = {}

        # TODO: Validate name length
        # if 'name' in data:
        #     if len(data['name']) < 3 or len(data['name']) > 200:
        #         errors['name'] = 'Name must be between 3 and 200 characters'

        # TODO: Validate SKU uniqueness
        # TODO: Validate price > 0
        # TODO: Validate stock_quantity >= 0
        # TODO: Validate category is in VALID_CATEGORIES

        # Return None if valid, errors dict if invalid
        return errors if errors else None

    def find_product_by_id(product_id):
        """Find product by ID."""
        # TODO: Implement this helper
        pass

    def find_product_by_sku(sku):
        """Find product by SKU."""
        # TODO: Implement this helper
        pass

    def calculate_order_total(items):
        """
        Calculate total amount for order items.

        TODO: Implement order total calculation
        STEPS:
        1. Initialize total = 0
        2. For each item in items:
        3.   Find product by product_id
        4.   If product not found, raise ValueError with product_id
        5.   Add (product['price'] * item['quantity']) to total
        6. Return total rounded to 2 decimals

        HINT: Use round(total, 2)
        HINT: Raise ValueError("Product not found: {id}") if product missing
        """
        # TODO: Implement total calculation
        pass

    def check_stock_availability(items):
        """
        Check if sufficient stock is available for all items.

        Returns:
            List of items with insufficient stock, or empty list if all OK

        TODO: Implement stock checking
        HINT: For each item, find product and check if stock_quantity >= item quantity
        HINT: Return list of dicts like: [{'product_id': 1, 'requested': 5, 'available': 3}]
        """
        # TODO: Implement stock checking
        pass

    # ============================================================================
    # PRODUCTS ENDPOINTS
    # ============================================================================

    @products_ns.route('/')
    class ProductList(Resource):
        """Products collection endpoint."""

        @products_ns.doc('list_products')
        @products_ns.marshal_list_with(product_model)
        def get(self):
            """
            List all products.

            TODO: Implement this endpoint
            STATUS CODE: 200 OK (default)
            """
            # TODO: Return products list
            pass

        @products_ns.doc('create_product')
        @products_ns.expect(product_model)
        @products_ns.response(201, 'Product created')
        @products_ns.response(400, 'Missing required fields')
        @products_ns.response(409, 'SKU already exists')
        @products_ns.response(422, 'Validation failed')
        def post(self):
            """
            Create a new product.

            TODO: Implement with proper error handling
            STEPS:
            1. Get request data
            2. Check required fields (sku, name, price, stock_quantity, category)
               - If missing, return 400 with create_error_response()
            3. Validate data using validate_product_data()
               - If errors, return 422 with error details
            4. Check SKU uniqueness
               - If duplicate, return 409 Conflict
            5. Generate new ID
            6. Add product to list
            7. Return product with 201 Created

            ERROR SCENARIOS:
            - Missing required field → 400 Bad Request
            - Invalid field values → 422 Unprocessable Entity
            - Duplicate SKU → 409 Conflict

            HINT: Use create_error_response('VALIDATION_ERROR', message, details, 422)
            HINT: Use create_error_response('CONFLICT', message, None, 409)
            """
            # TODO: Implement POST /products with proper error handling
            pass

    @products_ns.route('/<int:id>')
    @products_ns.response(404, 'Product not found')
    @products_ns.param('id', 'Product identifier')
    class ProductItem(Resource):
        """Single product endpoint."""

        @products_ns.doc('get_product')
        @products_ns.marshal_with(product_model)
        def get(self, id):
            """
            Get product by ID.

            TODO: Implement with proper 404 handling
            STEPS:
            1. Find product by ID
            2. If not found, return create_error_response('NOT_FOUND', message, None, 404)
            3. Return product with 200 OK

            ERROR SCENARIO:
            - Product doesn't exist → 404 Not Found
            """
            # TODO: Implement GET /products/{id}
            pass

        @products_ns.doc('update_product')
        @products_ns.expect(product_model)
        @products_ns.marshal_with(product_model)
        @products_ns.response(422, 'Validation failed')
        @products_ns.response(409, 'SKU conflict')
        def put(self, id):
            """
            Update product.

            TODO: Implement with validation
            STEPS:
            1. Find product (return 404 if not found)
            2. Get request data
            3. Validate data using validate_product_data(data, is_update=True, existing_product=product)
            4. If validation errors, return 422 with details
            5. Update product fields
            6. Return updated product with 200 OK

            ERROR SCENARIOS:
            - Product not found → 404
            - Invalid values → 422
            - SKU conflict → 409
            """
            # TODO: Implement PUT /products/{id}
            pass

        @products_ns.doc('delete_product')
        @products_ns.response(204, 'Product deleted')
        def delete(self, id):
            """
            Delete product.

            TODO: Implement DELETE
            STATUS CODE: 204 No Content on success
            """
            # TODO: Implement DELETE /products/{id}
            pass

    # ============================================================================
    # ORDERS ENDPOINTS
    # ============================================================================

    @orders_ns.route('/')
    class OrderList(Resource):
        """Orders collection endpoint."""

        @orders_ns.doc('list_orders')
        @orders_ns.marshal_list_with(order_model)
        def get(self):
            """List all orders."""
            # TODO: Implement GET /orders
            pass

        @orders_ns.doc('create_order')
        @orders_ns.expect(order_model)
        @orders_ns.response(201, 'Order created')
        @orders_ns.response(400, 'Invalid request data')
        @orders_ns.response(404, 'Product not found')
        @orders_ns.response(409, 'Insufficient stock')
        @orders_ns.response(422, 'Validation failed')
        def post(self):
            """
            Create a new order.

            TODO: Implement with comprehensive validation
            STEPS:
            1. Get request data
            2. Validate required fields (customer_email, items, total_amount)
               - If missing, return 400
            3. Validate email format
               - If invalid, return 422 with error details
            4. Validate items list is not empty
               - If empty, return 400
            5. Calculate actual total using calculate_order_total()
               - If product not found, return 404
            6. Check if provided total_amount matches calculated total
               - If mismatch, return 400 with both values in details
            7. Check stock availability using check_stock_availability()
               - If insufficient, return 409 with details of what's unavailable
            8. Deduct stock from products
            9. Create order with status 'pending'
            10. Set created_at timestamp
            11. Add to orders list
            12. Return order with 201 Created

            ERROR SCENARIOS:
            - Missing fields → 400 Bad Request
            - Invalid email → 422 Unprocessable Entity
            - Product doesn't exist → 404 Not Found
            - Total mismatch → 400 Bad Request
            - Insufficient stock → 409 Conflict

            HINT: For stock, return error like:
            create_error_response(
                'INSUFFICIENT_STOCK',
                'Insufficient stock for some items',
                {'unavailable': [{'product_id': 1, 'requested': 5, 'available': 3}]},
                409
            )
            """
            # TODO: Implement POST /orders with all validations
            pass

    @orders_ns.route('/<int:id>')
    @orders_ns.response(404, 'Order not found')
    @orders_ns.param('id', 'Order identifier')
    class OrderItem(Resource):
        """Single order endpoint."""

        @orders_ns.doc('get_order')
        @orders_ns.marshal_with(order_model)
        def get(self, id):
            """Get order by ID."""
            # TODO: Implement GET /orders/{id}
            pass

    @orders_ns.route('/<int:id>/cancel')
    @orders_ns.response(404, 'Order not found')
    @orders_ns.response(400, 'Order already cancelled')
    @orders_ns.param('id', 'Order identifier')
    class OrderCancel(Resource):
        """Cancel order endpoint."""

        @orders_ns.doc('cancel_order')
        @orders_ns.marshal_with(order_model)
        def patch(self, id):
            """
            Cancel an order and restore stock.

            TODO: Implement order cancellation
            STEPS:
            1. Find order (return 404 if not found)
            2. Check if already cancelled
               - If status is 'cancelled', return 400
            3. Restore stock for all items in the order
            4. Set status to 'cancelled'
            5. Return updated order with 200 OK

            ERROR SCENARIOS:
            - Order not found → 404
            - Already cancelled → 400
            """
            # TODO: Implement PATCH /orders/{id}/cancel
            pass

    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(products_ns, path='/products')
    api.add_namespace(orders_ns, path='/orders')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("PRODUCT CATALOG API - Exercise 2: Status Codes & Error Handling")
    print("="*70)
    print("📚 Learning Objectives:")
    print("  - Use correct status codes for each scenario")
    print("  - Return structured error responses")
    print("  - Implement input validation (format, type, required)")
    print("  - Implement business logic validation (stock, uniqueness)")
    print("\n🎯 Status Codes to Master:")
    print("  200 - Successful GET/PUT/PATCH")
    print("  201 - Resource created")
    print("  204 - Resource deleted")
    print("  400 - Bad request (malformed, missing required)")
    print("  404 - Resource not found")
    print("  409 - Conflict (duplicate, insufficient stock)")
    print("  422 - Validation failed (invalid values)")
    print("\n🧪 Test These Scenarios:")
    print("  1. Create product with duplicate SKU → 409")
    print("  2. Create product with negative price → 422")
    print("  3. Get non-existent product → 404")
    print("  4. Create order with insufficient stock → 409")
    print("  5. Create order with invalid email → 422")
    print("  6. Create order with total mismatch → 400")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
