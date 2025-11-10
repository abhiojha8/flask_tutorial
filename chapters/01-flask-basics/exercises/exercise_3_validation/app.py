"""
Exercise 3: Input Validation and Flask-RESTX

Learning Objectives:
- Use Flask-RESTX for API structure
- Define data models for validation
- Validate input automatically
- Generate Swagger documentation

TODO: Complete the marked sections!
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace

def create_app():
    """Create the Flask application with Flask-RESTX."""
    app = Flask(__name__)

    # TODO 1: Initialize Flask-RESTX Api
    # Create an Api instance with:
    # - title='Product API'
    # - version='1.0'
    # - description='A product management API with validation'
    # - doc='/swagger'
    # Hint: api = Api(app, title='...', ...)


    # In-memory product storage
    products = []

    # TODO 2: Create a namespace for products
    # Hint: products_ns = Namespace('products', description='Product operations')


    # TODO 3: Define the product input model
    # Create a model with these fields:
    # - name: String, required, description='Product name'
    # - price: Float, required, description='Product price'
    # - category: String, enum=['electronics', 'books', 'clothing']
    # - in_stock: Boolean, default=True
    # Hint: product_input = api.model('ProductInput', { ... })


    # TODO 4: Define the product output model
    # Inherit from product_input and add:
    # - id: Integer, readonly=True
    # - created_at: String, readonly=True
    # Hint: product_output = api.inherit('ProductOutput', product_input, { ... })


    # TODO 5: Create ProductList Resource
    # Create a class that handles /products/ endpoint
    # with GET and POST methods
    #
    # @products_ns.route('/')
    # class ProductList(Resource):
    #     GET method should:
    #     - Use @products_ns.marshal_list_with(product_output)
    #     - Return the products list
    #
    #     POST method should:
    #     - Use @products_ns.expect(product_input, validate=True)
    #     - Use @products_ns.marshal_with(product_output, code=201)
    #     - Create new product with id and created_at
    #     - Add to products list
    #     - Return created product with 201 status


    # TODO 6: Create Product Resource
    # Create a class that handles /products/<id> endpoint
    # with GET, PUT, DELETE methods
    #
    # @products_ns.route('/<int:id>')
    # class Product(Resource):
    #     GET method should:
    #     - Find product by id
    #     - Return 404 if not found (use api.abort(404, 'Product not found'))
    #     - Return product with @marshal_with
    #
    #     PUT method should:
    #     - Find product by id
    #     - Return 404 if not found
    #     - Update product with new data
    #     - Return updated product
    #
    #     DELETE method should:
    #     - Find product by id
    #     - Return 404 if not found
    #     - Remove from list
    #     - Return '', 204


    # TODO 7: Register the namespace
    # Hint: api.add_namespace(products_ns, path='/products')


    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 3: Input Validation with Flask-RESTX")
    print("="*50)
    print("Swagger UI: http://localhost:5000/swagger")
    print("\nTry creating a product with invalid data:")
    print("  - Missing required field (name or price)")
    print("  - Invalid category (not in enum)")
    print("  - Wrong data type (string for price)")
    print("\nSee automatic validation in action!")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
