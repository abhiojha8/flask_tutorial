"""
Exercise 2: Status Codes & Error Handling - E-commerce Product Catalog API - SOLUTION

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
        error_dict = {
            'error': {
                'code': code,
                'message': message,
                'details': details,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'path': request.path
            }
        }
        return error_dict, status_code

    # ============================================================================
    # VALIDATION HELPERS
    # ============================================================================

    def validate_email(email):
        """
        Validate email format.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_product_data(data, is_update=False, existing_product=None):
        """
        Validate product data and return detailed errors.

        Args:
            data: Product data to validate
            is_update: Whether this is an update operation
            existing_product: Existing product (for updates)

        Returns:
            Dictionary of field errors, or None if valid
        """
        errors = {}

        # Validate name length
        if 'name' in data:
            if len(data['name']) < 3 or len(data['name']) > 200:
                errors['name'] = 'Name must be between 3 and 200 characters'

        # Validate SKU uniqueness
        if 'sku' in data:
            for product in products:
                # Skip current product when updating
                if is_update and existing_product and product['id'] == existing_product['id']:
                    continue
                if product['sku'] == data['sku']:
                    errors['sku'] = 'SKU already exists'
                    break

        # Validate price > 0
        if 'price' in data:
            if data['price'] <= 0:
                errors['price'] = 'Price must be greater than 0'

        # Validate stock_quantity >= 0
        if 'stock_quantity' in data:
            if data['stock_quantity'] < 0:
                errors['stock_quantity'] = 'Stock quantity must be greater than or equal to 0'

        # Validate category is in VALID_CATEGORIES
        if 'category' in data:
            if data['category'] not in VALID_CATEGORIES:
                errors['category'] = f'Category must be one of: {", ".join(VALID_CATEGORIES)}'

        # Return None if valid, errors dict if invalid
        return errors if errors else None

    def find_product_by_id(product_id):
        """Find product by ID."""
        for product in products:
            if product['id'] == product_id:
                return product
        return None

    def find_product_by_sku(sku):
        """Find product by SKU."""
        for product in products:
            if product['sku'] == sku:
                return product
        return None

    def calculate_order_total(items):
        """
        Calculate total amount for order items.
        """
        total = 0
        for item in items:
            product = find_product_by_id(item['product_id'])
            if not product:
                raise ValueError(f"Product not found: {item['product_id']}")
            total += product['price'] * item['quantity']
        return round(total, 2)

    def check_stock_availability(items):
        """
        Check if sufficient stock is available for all items.

        Returns:
            List of items with insufficient stock, or empty list if all OK
        """
        unavailable = []
        for item in items:
            product = find_product_by_id(item['product_id'])
            if product and product['stock_quantity'] < item['quantity']:
                unavailable.append({
                    'product_id': item['product_id'],
                    'requested': item['quantity'],
                    'available': product['stock_quantity']
                })
        return unavailable

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

            STATUS CODE: 200 OK (default)
            """
            return products

        @products_ns.doc('create_product')
        @products_ns.expect(product_model)
        @products_ns.response(201, 'Product created')
        @products_ns.response(400, 'Missing required fields')
        @products_ns.response(409, 'SKU already exists')
        @products_ns.response(422, 'Validation failed')
        def post(self):
            """
            Create a new product.

            ERROR SCENARIOS:
            - Missing required field → 400 Bad Request
            - Invalid field values → 422 Unprocessable Entity
            - Duplicate SKU → 409 Conflict
            """
            data = request.json

            # Check required fields
            required_fields = ['sku', 'name', 'price', 'stock_quantity', 'category']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return create_error_response(
                    'BAD_REQUEST',
                    'Missing required fields',
                    {'missing_fields': missing_fields},
                    400
                )

            # Validate data
            validation_errors = validate_product_data(data)
            if validation_errors:
                # Check if SKU error (409) vs other validation errors (422)
                if 'sku' in validation_errors and validation_errors['sku'] == 'SKU already exists':
                    return create_error_response(
                        'CONFLICT',
                        'SKU already exists',
                        {'sku': data['sku']},
                        409
                    )
                return create_error_response(
                    'VALIDATION_ERROR',
                    'Validation failed',
                    validation_errors,
                    422
                )

            # Generate new ID
            new_id = max([p['id'] for p in products], default=0) + 1

            # Create product
            product = {
                'id': new_id,
                'sku': data['sku'],
                'name': data['name'],
                'description': data.get('description', ''),
                'price': data['price'],
                'stock_quantity': data['stock_quantity'],
                'category': data['category']
            }

            products.append(product)
            return product, 201

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

            ERROR SCENARIO:
            - Product doesn't exist → 404 Not Found
            """
            product = find_product_by_id(id)
            if not product:
                return create_error_response(
                    'NOT_FOUND',
                    f'Product with ID {id} not found',
                    None,
                    404
                )
            return product

        @products_ns.doc('update_product')
        @products_ns.expect(product_model)
        @products_ns.marshal_with(product_model)
        @products_ns.response(422, 'Validation failed')
        @products_ns.response(409, 'SKU conflict')
        def put(self, id):
            """
            Update product.

            ERROR SCENARIOS:
            - Product not found → 404
            - Invalid values → 422
            - SKU conflict → 409
            """
            product = find_product_by_id(id)
            if not product:
                return create_error_response(
                    'NOT_FOUND',
                    f'Product with ID {id} not found',
                    None,
                    404
                )

            data = request.json

            # Validate data
            validation_errors = validate_product_data(data, is_update=True, existing_product=product)
            if validation_errors:
                # Check if SKU error (409) vs other validation errors (422)
                if 'sku' in validation_errors and validation_errors['sku'] == 'SKU already exists':
                    return create_error_response(
                        'CONFLICT',
                        'SKU already exists',
                        {'sku': data.get('sku')},
                        409
                    )
                return create_error_response(
                    'VALIDATION_ERROR',
                    'Validation failed',
                    validation_errors,
                    422
                )

            # Update product fields
            if 'sku' in data:
                product['sku'] = data['sku']
            if 'name' in data:
                product['name'] = data['name']
            if 'description' in data:
                product['description'] = data['description']
            if 'price' in data:
                product['price'] = data['price']
            if 'stock_quantity' in data:
                product['stock_quantity'] = data['stock_quantity']
            if 'category' in data:
                product['category'] = data['category']

            return product

        @products_ns.doc('delete_product')
        @products_ns.response(204, 'Product deleted')
        def delete(self, id):
            """
            Delete product.

            STATUS CODE: 204 No Content on success
            """
            product = find_product_by_id(id)
            if not product:
                return create_error_response(
                    'NOT_FOUND',
                    f'Product with ID {id} not found',
                    None,
                    404
                )

            products.remove(product)
            return '', 204

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
            return orders

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

            ERROR SCENARIOS:
            - Missing fields → 400 Bad Request
            - Invalid email → 422 Unprocessable Entity
            - Product doesn't exist → 404 Not Found
            - Total mismatch → 400 Bad Request
            - Insufficient stock → 409 Conflict
            """
            data = request.json

            # Validate required fields
            required_fields = ['customer_email', 'items', 'total_amount']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return create_error_response(
                    'BAD_REQUEST',
                    'Missing required fields',
                    {'missing_fields': missing_fields},
                    400
                )

            # Validate email format
            if not validate_email(data['customer_email']):
                return create_error_response(
                    'VALIDATION_ERROR',
                    'Validation failed',
                    {'customer_email': 'Invalid email format'},
                    422
                )

            # Validate items list is not empty
            if not data['items'] or len(data['items']) == 0:
                return create_error_response(
                    'BAD_REQUEST',
                    'Items list cannot be empty',
                    None,
                    400
                )

            # Calculate actual total
            try:
                calculated_total = calculate_order_total(data['items'])
            except ValueError as e:
                return create_error_response(
                    'NOT_FOUND',
                    str(e),
                    None,
                    404
                )

            # Check if provided total matches calculated total
            if abs(data['total_amount'] - calculated_total) > 0.01:  # Allow small floating point differences
                return create_error_response(
                    'BAD_REQUEST',
                    'Total amount mismatch',
                    {
                        'provided': data['total_amount'],
                        'calculated': calculated_total
                    },
                    400
                )

            # Check stock availability
            unavailable = check_stock_availability(data['items'])
            if unavailable:
                return create_error_response(
                    'INSUFFICIENT_STOCK',
                    'Insufficient stock for some items',
                    {'unavailable': unavailable},
                    409
                )

            # Deduct stock from products
            for item in data['items']:
                product = find_product_by_id(item['product_id'])
                product['stock_quantity'] -= item['quantity']

            # Create order
            new_id = max([o['id'] for o in orders], default=0) + 1
            order = {
                'id': new_id,
                'customer_email': data['customer_email'],
                'items': data['items'],
                'total_amount': data['total_amount'],
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }

            orders.append(order)
            return order, 201

    @orders_ns.route('/<int:id>')
    @orders_ns.response(404, 'Order not found')
    @orders_ns.param('id', 'Order identifier')
    class OrderItem(Resource):
        """Single order endpoint."""

        @orders_ns.doc('get_order')
        @orders_ns.marshal_with(order_model)
        def get(self, id):
            """Get order by ID."""
            order = None
            for o in orders:
                if o['id'] == id:
                    order = o
                    break

            if not order:
                return create_error_response(
                    'NOT_FOUND',
                    f'Order with ID {id} not found',
                    None,
                    404
                )
            return order

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

            ERROR SCENARIOS:
            - Order not found → 404
            - Already cancelled → 400
            """
            order = None
            for o in orders:
                if o['id'] == id:
                    order = o
                    break

            if not order:
                return create_error_response(
                    'NOT_FOUND',
                    f'Order with ID {id} not found',
                    None,
                    404
                )

            # Check if already cancelled
            if order['status'] == 'cancelled':
                return create_error_response(
                    'BAD_REQUEST',
                    'Order is already cancelled',
                    None,
                    400
                )

            # Restore stock for all items
            for item in order['items']:
                product = find_product_by_id(item['product_id'])
                if product:
                    product['stock_quantity'] += item['quantity']

            # Set status to cancelled
            order['status'] = 'cancelled'

            return order

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
