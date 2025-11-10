"""
Exercise 3 Solution: Input Validation and Flask-RESTX

This solution demonstrates:
- Using Flask-RESTX for API structure
- Defining data models for validation
- Automatic input validation
- Generating Swagger documentation
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime

def create_app():
    """Create the Flask application with Flask-RESTX."""
    app = Flask(__name__)

    # TODO 1: Initialize Flask-RESTX Api
    api = Api(
        app,
        title='Product API',
        version='1.0',
        description='A product management API with validation',
        doc='/swagger'
    )

    # In-memory product storage
    products = []

    # TODO 2: Create a namespace for products
    products_ns = Namespace('products', description='Product operations')

    # TODO 3: Define the product input model
    product_input = api.model('ProductInput', {
        'name': fields.String(required=True, description='Product name'),
        'price': fields.Float(required=True, description='Product price'),
        'category': fields.String(
            required=True,
            description='Product category',
            enum=['electronics', 'books', 'clothing']
        ),
        'in_stock': fields.Boolean(default=True, description='Stock availability')
    })

    # TODO 4: Define the product output model
    product_output = api.inherit('ProductOutput', product_input, {
        'id': fields.Integer(readonly=True, description='Product ID'),
        'created_at': fields.String(readonly=True, description='Creation timestamp')
    })

    # Helper function
    def find_product(product_id):
        """Find a product by ID."""
        for product in products:
            if product['id'] == product_id:
                return product
        return None

    # TODO 5: Create ProductList Resource
    @products_ns.route('/')
    class ProductList(Resource):
        @products_ns.doc('list_products')
        @products_ns.marshal_list_with(product_output)
        def get(self):
            """List all products."""
            return products

        @products_ns.doc('create_product')
        @products_ns.expect(product_input, validate=True)
        @products_ns.marshal_with(product_output, code=201)
        def post(self):
            """Create a new product."""
            data = api.payload

            # Create new product
            new_product = {
                'id': len(products) + 1,
                'name': data['name'],
                'price': data['price'],
                'category': data['category'],
                'in_stock': data.get('in_stock', True),
                'created_at': datetime.now().isoformat()
            }

            products.append(new_product)
            return new_product, 201

    # TODO 6: Create Product Resource
    @products_ns.route('/<int:id>')
    @products_ns.param('id', 'The product identifier')
    @products_ns.response(404, 'Product not found')
    class Product(Resource):
        @products_ns.doc('get_product')
        @products_ns.marshal_with(product_output)
        def get(self, id):
            """Get a product by ID."""
            product = find_product(id)
            if not product:
                api.abort(404, f'Product {id} not found')
            return product

        @products_ns.doc('update_product')
        @products_ns.expect(product_input, validate=True)
        @products_ns.marshal_with(product_output)
        def put(self, id):
            """Update a product."""
            product = find_product(id)
            if not product:
                api.abort(404, f'Product {id} not found')

            data = api.payload
            product['name'] = data['name']
            product['price'] = data['price']
            product['category'] = data['category']
            product['in_stock'] = data.get('in_stock', True)

            return product

        @products_ns.doc('delete_product')
        @products_ns.response(204, 'Product deleted')
        def delete(self, id):
            """Delete a product."""
            product = find_product(id)
            if not product:
                api.abort(404, f'Product {id} not found')

            products.remove(product)
            return '', 204

    # TODO 7: Register the namespace
    api.add_namespace(products_ns, path='/products')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 3 Solution: Input Validation with Flask-RESTX")
    print("="*50)
    print("Swagger UI: http://localhost:5000/swagger")
    print("\nTry creating a product with invalid data:")
    print("  - Missing required field (name or price)")
    print("  - Invalid category (not in enum)")
    print("  - Wrong data type (string for price)")
    print("\nSee automatic validation in action!")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
