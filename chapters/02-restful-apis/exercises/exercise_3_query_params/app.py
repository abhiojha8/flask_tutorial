"""
Exercise 3: Query Parameters & Filtering - Advanced Product Search API

OBJECTIVE:
Master query parameters for filtering, sorting, searching, and pagination.

WHAT YOU'LL BUILD:
- Product catalog with advanced query capabilities
- Filtering by multiple fields
- Full-text search
- Multi-field sorting
- Pagination with metadata
- Field selection

LEARNING GOALS:
- Parse and apply query parameters
- Filter data by field values
- Implement search across multiple fields
- Sort by multiple criteria
- Paginate results with metadata
- Select specific fields to return
- Combine multiple query features

QUERY PARAMETERS TO IMPLEMENT:
Filtering: ?category=Electronics&min_price=100&max_price=1000
Search: ?search=laptop&name_contains=pro
Sorting: ?sort=price,-rating (- means descending)
Pagination: ?page=1&per_page=20
Fields: ?fields=id,name,price

TODO CHECKLIST:
[ ] Implement filtering by category, brand, price range, stock, rating
[ ] Implement search across name and description
[ ] Implement sorting (single and multiple fields)
[ ] Implement pagination with metadata
[ ] Implement field selection
[ ] Combine all features together
[ ] Return empty array (not 404) for no results
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from datetime import datetime

def create_app():
    """
    Create the Product Search API with advanced querying.

    This API demonstrates query parameters, filtering, sorting, and pagination.
    """
    app = Flask(__name__)
    CORS(app)

    api = Api(
        app,
        version='3.0',
        title='Product Search API',
        description='Exercise 3: Master Query Parameters and Filtering',
        doc='/swagger'
    )

    # ============================================================================
    # DATA MODELS
    # ============================================================================

    products_ns = Namespace('products', description='Product search and filtering')

    product_model = products_ns.model('Product', {
        'id': fields.Integer(description='Product ID'),
        'name': fields.String(description='Product name'),
        'description': fields.String(description='Product description'),
        'price': fields.Float(description='Product price'),
        'category': fields.String(description='Product category'),
        'brand': fields.String(description='Product brand'),
        'stock': fields.Integer(description='Stock quantity'),
        'rating': fields.Float(description='Average rating'),
        'tags': fields.List(fields.String, description='Product tags'),
        'featured': fields.Boolean(description='Featured product'),
        'created_at': fields.String(description='Creation date')
    })

    pagination_model = products_ns.model('Pagination', {
        'page': fields.Integer(description='Current page number'),
        'per_page': fields.Integer(description='Items per page'),
        'total': fields.Integer(description='Total items'),
        'pages': fields.Integer(description='Total pages'),
        'has_next': fields.Boolean(description='Has next page'),
        'has_prev': fields.Boolean(description='Has previous page')
    })

    products_response_model = products_ns.model('ProductsResponse', {
        'data': fields.List(fields.Nested(product_model)),
        'pagination': fields.Nested(pagination_model),
        'filters_applied': fields.Raw(description='Filters that were applied')
    })

    # ============================================================================
    # SAMPLE DATA - Diverse product catalog
    # ============================================================================

    products = [
        {
            'id': 1, 'name': 'Premium Laptop', 'description': 'High-performance laptop for professionals',
            'price': 1299.99, 'category': 'Electronics', 'brand': 'TechCorp', 'stock': 15,
            'rating': 4.5, 'tags': ['computer', 'portable', 'professional'], 'featured': True,
            'created_at': '2024-01-15'
        },
        {
            'id': 2, 'name': 'Wireless Mouse', 'description': 'Ergonomic wireless mouse',
            'price': 29.99, 'category': 'Electronics', 'brand': 'TechCorp', 'stock': 50,
            'rating': 4.2, 'tags': ['accessory', 'wireless'], 'featured': False,
            'created_at': '2024-01-20'
        },
        {
            'id': 3, 'name': 'Running Shoes', 'description': 'Comfortable running shoes',
            'price': 89.99, 'category': 'Sports', 'brand': 'SportMax', 'stock': 30,
            'rating': 4.7, 'tags': ['shoes', 'running', 'fitness'], 'featured': True,
            'created_at': '2024-02-01'
        },
        {
            'id': 4, 'name': 'Coffee Maker', 'description': 'Automatic coffee maker with timer',
            'price': 79.99, 'category': 'Home & Garden', 'brand': 'HomeEssentials', 'stock': 20,
            'rating': 4.0, 'tags': ['kitchen', 'appliance'], 'featured': False,
            'created_at': '2024-02-10'
        },
        {
            'id': 5, 'name': 'Python Programming Book', 'description': 'Comprehensive Python guide',
            'price': 49.99, 'category': 'Books', 'brand': 'TechPublishers', 'stock': 100,
            'rating': 4.8, 'tags': ['programming', 'education', 'python'], 'featured': True,
            'created_at': '2024-01-05'
        },
        {
            'id': 6, 'name': 'Yoga Mat', 'description': 'Non-slip yoga mat',
            'price': 24.99, 'category': 'Sports', 'brand': 'FitLife', 'stock': 40,
            'rating': 4.3, 'tags': ['yoga', 'fitness', 'exercise'], 'featured': False,
            'created_at': '2024-02-15'
        },
        {
            'id': 7, 'name': 'Smart Watch', 'description': 'Fitness tracking smart watch',
            'price': 199.99, 'category': 'Electronics', 'brand': 'TechCorp', 'stock': 25,
            'rating': 4.4, 'tags': ['wearable', 'fitness', 'smart'], 'featured': True,
            'created_at': '2024-01-25'
        },
        {
            'id': 8, 'name': 'Desk Lamp', 'description': 'LED desk lamp with adjustable brightness',
            'price': 34.99, 'category': 'Home & Garden', 'brand': 'HomeEssentials', 'stock': 35,
            'rating': 4.1, 'tags': ['lighting', 'office'], 'featured': False,
            'created_at': '2024-02-20'
        },
        {
            'id': 9, 'name': 'Water Bottle', 'description': 'Insulated stainless steel water bottle',
            'price': 19.99, 'category': 'Sports', 'brand': 'SportMax', 'stock': 60,
            'rating': 4.6, 'tags': ['hydration', 'fitness'], 'featured': False,
            'created_at': '2024-02-05'
        },
        {
            'id': 10, 'name': 'Mechanical Keyboard', 'description': 'RGB mechanical gaming keyboard',
            'price': 129.99, 'category': 'Electronics', 'brand': 'GameTech', 'stock': 18,
            'rating': 4.9, 'tags': ['gaming', 'computer', 'rgb'], 'featured': True,
            'created_at': '2024-01-30'
        }
    ]

    # ============================================================================
    # FILTERING HELPERS
    # ============================================================================

    def apply_filters(products_list, params):
        """
        Apply filters to products based on query parameters.

        TODO: Implement filtering logic
        FILTERS TO SUPPORT:
        - category: exact match
        - brand: exact match
        - min_price: price >= min_price
        - max_price: price <= max_price
        - in_stock: stock > 0 (if in_stock=true)
        - rating_gte: rating >= value
        - featured: exact match (convert to boolean)

        Args:
            products_list: List of products to filter
            params: Query parameters dict

        Returns:
            Filtered list of products

        HINT: Start with filtered = products_list.copy()
        HINT: For each filter, if it exists in params:
              filtered = [p for p in filtered if condition]
        HINT: For in_stock, check if params.get('in_stock') == 'true'
        HINT: For featured, check if params.get('featured') == 'true'
        """
        # TODO: Implement filtering
        # Example structure:
        # filtered = products_list.copy()
        # if 'category' in params:
        #     filtered = [p for p in filtered if p['category'] == params['category']]
        # if 'min_price' in params:
        #     min_price = float(params['min_price'])
        #     filtered = [p for p in filtered if p['price'] >= min_price]
        # ... more filters
        # return filtered
        pass

    def apply_search(products_list, params):
        """
        Apply search to products.

        TODO: Implement search logic
        SEARCH PARAMETERS:
        - search: search in name AND description (case-insensitive)
        - name_contains: search only in name (case-insensitive)
        - tags_contains: search in tags list (case-insensitive)

        HINT: Use .lower() for case-insensitive search
        HINT: Use 'keyword' in text.lower() for substring search
        HINT: For tags, check if any tag contains the keyword
        """
        # TODO: Implement search
        # if 'search' in params:
        #     keyword = params['search'].lower()
        #     products_list = [p for p in products_list
        #                      if keyword in p['name'].lower()
        #                      or keyword in p['description'].lower()]
        # ... more search options
        pass

    def apply_sorting(products_list, params):
        """
        Apply sorting to products.

        TODO: Implement sorting logic
        SORTING PARAMETER:
        - sort: comma-separated fields (e.g., "price,-rating")
        - Fields with '-' prefix are sorted descending
        - Fields without prefix are sorted ascending

        EXAMPLES:
        ?sort=price          → Sort by price ascending
        ?sort=-price         → Sort by price descending
        ?sort=rating,-price  → Sort by rating asc, then price desc

        HINT: Split params['sort'] by comma
        HINT: For each field, check if it starts with '-'
        HINT: Use sorted() with multiple keys
        HINT: For multiple fields, sort in reverse order:
              First sort by last field, then by second-to-last, etc.

        ADVANCED HINT:
        sort_fields = params.get('sort', '').split(',')
        for field in reversed(sort_fields):  # Process in reverse
            if field.startswith('-'):
                actual_field = field[1:]
                products_list = sorted(products_list, key=lambda x: x[actual_field], reverse=True)
            else:
                products_list = sorted(products_list, key=lambda x: x[field])
        """
        # TODO: Implement sorting
        pass

    def apply_pagination(products_list, params):
        """
        Apply pagination to products.

        TODO: Implement pagination logic
        PARAMETERS:
        - page: page number (default 1)
        - per_page: items per page (default 10, max 100)

        Returns:
            Tuple of (paginated_products, pagination_metadata)

        HINT: page = int(params.get('page', 1))
        HINT: per_page = min(int(params.get('per_page', 10)), 100)
        HINT: start_idx = (page - 1) * per_page
        HINT: end_idx = start_idx + per_page
        HINT: paginated = products_list[start_idx:end_idx]

        HINT: Build metadata dict:
        {
            'page': current page,
            'per_page': items per page,
            'total': total items,
            'pages': total pages (use math.ceil),
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
        """
        # TODO: Implement pagination
        # Return (paginated_list, metadata_dict)
        pass

    def apply_field_selection(products_list, params):
        """
        Select specific fields from products.

        TODO: Implement field selection
        PARAMETERS:
        - fields: comma-separated field names (e.g., "id,name,price")

        HINT: If 'fields' not in params, return products_list unchanged
        HINT: Split params['fields'] by comma to get field list
        HINT: For each product, create new dict with only selected fields
        HINT: Use dict comprehension: {k: product[k] for k in field_list if k in product}
        """
        # TODO: Implement field selection
        pass

    def get_applied_filters(params):
        """
        Get a dict of filters that were actually applied.

        TODO: Return dict of all filter parameters that were used
        HINT: Check for: category, brand, min_price, max_price, in_stock,
              rating_gte, featured, search, name_contains, tags_contains, sort
        HINT: Only include params that exist and are not empty
        """
        # TODO: Return dict of applied filters
        pass

    # ============================================================================
    # PRODUCTS ENDPOINT
    # ============================================================================

    @products_ns.route('/')
    class ProductList(Resource):
        """Products with advanced querying."""

        @products_ns.doc('search_products', params={
            'category': 'Filter by category',
            'brand': 'Filter by brand',
            'min_price': 'Minimum price',
            'max_price': 'Maximum price',
            'in_stock': 'Only in-stock items (true/false)',
            'rating_gte': 'Minimum rating',
            'featured': 'Featured products only (true/false)',
            'search': 'Search in name and description',
            'name_contains': 'Search in name only',
            'tags_contains': 'Search in tags',
            'sort': 'Sort by fields (comma-separated, - for desc)',
            'page': 'Page number (default 1)',
            'per_page': 'Items per page (default 10, max 100)',
            'fields': 'Select specific fields (comma-separated)'
        })
        def get(self):
            """
            Search and filter products with pagination.

            TODO: Implement the complete query pipeline
            STEPS:
            1. Start with all products
            2. Apply filters using apply_filters()
            3. Apply search using apply_search()
            4. Apply sorting using apply_sorting()
            5. Apply pagination using apply_pagination() - get (data, metadata)
            6. Apply field selection using apply_field_selection()
            7. Build response with data, pagination, and filters_applied
            8. Return response

            IMPORTANT:
            - Empty results should return [] with 200, NOT 404
            - Invalid query params (e.g., invalid field name) should return 400

            HINT: Use request.args to get query parameters
            HINT: response = {
                'data': selected_products,
                'pagination': metadata,
                'filters_applied': get_applied_filters(request.args)
            }
            """
            # TODO: Implement GET /products with full query support
            # params = request.args
            # filtered = apply_filters(products, params)
            # searched = apply_search(filtered, params)
            # sorted_products = apply_sorting(searched, params)
            # paginated, pagination_meta = apply_pagination(sorted_products, params)
            # result = apply_field_selection(paginated, params)
            # return {
            #     'data': result,
            #     'pagination': pagination_meta,
            #     'filters_applied': get_applied_filters(params)
            # }
            pass

    @products_ns.route('/<int:id>')
    @products_ns.param('id', 'Product identifier')
    class ProductItem(Resource):
        """Single product endpoint."""

        @products_ns.doc('get_product')
        @products_ns.marshal_with(product_model)
        def get(self, id):
            """
            Get a single product by ID.

            TODO: Implement this endpoint
            HINT: Find product, return 404 if not found
            """
            # TODO: Implement GET /products/{id}
            pass

    # ============================================================================
    # REGISTER NAMESPACE
    # ============================================================================

    api.add_namespace(products_ns, path='/products')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("PRODUCT SEARCH API - Exercise 3: Query Parameters & Filtering")
    print("="*70)
    print("📚 Learning Objectives:")
    print("  - Parse and apply query parameters")
    print("  - Filter by multiple criteria")
    print("  - Implement full-text search")
    print("  - Sort by multiple fields")
    print("  - Paginate with metadata")
    print("  - Select specific fields")
    print("\n🎯 Query Examples to Try:")
    print("  Filtering:")
    print("    GET /products?category=Electronics")
    print("    GET /products?min_price=50&max_price=200")
    print("    GET /products?rating_gte=4.5&in_stock=true")
    print("\n  Search:")
    print("    GET /products?search=laptop")
    print("    GET /products?name_contains=book")
    print("    GET /products?tags_contains=fitness")
    print("\n  Sorting:")
    print("    GET /products?sort=price          (ascending)")
    print("    GET /products?sort=-rating        (descending)")
    print("    GET /products?sort=category,-price")
    print("\n  Pagination:")
    print("    GET /products?page=1&per_page=5")
    print("\n  Field Selection:")
    print("    GET /products?fields=id,name,price")
    print("\n  Combined:")
    print("    GET /products?category=Electronics&min_price=100&sort=-rating&page=1&per_page=5")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
