"""
Exercise 5: Advanced Swagger Documentation

Learning Objectives:
- Document API endpoints thoroughly
- Use response models
- Add examples to models
- Document query parameters
- Create detailed API documentation

TODO: Complete the marked sections to create comprehensive API docs!
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime
import uuid

def create_app():
    """Create the Flask application."""
    app = Flask(__name__)

    # TODO 1: Create Api with comprehensive metadata
    # Add these fields:
    # - title='Book Library API'
    # - version='1.0'
    # - description='A comprehensive API for managing a book library with detailed documentation'
    # - doc='/swagger'
    # - authorizations (optional): For future authentication
    # Hint: api = Api(app, title='...', version='...', description='...')


    books_ns = Namespace('books', description='Book management operations')

    # TODO 2: Create detailed book input model with examples
    # Fields to include:
    # - title: String, required, example='The Great Gatsby'
    # - author: String, required, example='F. Scott Fitzgerald'
    # - isbn: String, required, pattern for ISBN-13, example='978-0743273565'
    # - published_year: Integer, min=1000, max=2024, example=1925
    # - genre: String, enum=['fiction', 'non-fiction', 'sci-fi', 'mystery', 'romance']
    # - pages: Integer, min=1, example=180
    # - available: Boolean, default=True, description='Whether book is available for borrowing'
    # Hint: book_input = api.model('BookInput', {
    #     'title': fields.String(required=True, description='Book title', example='...'),
    #     ...
    # })


    # TODO 3: Create detailed book output model
    # Inherit from book_input and add:
    # - id: String, readonly=True, description='Unique book identifier (UUID)'
    # - created_at: String, readonly=True, description='Book creation timestamp (ISO 8601)'
    # - updated_at: String, readonly=True, description='Last update timestamp (ISO 8601)'
    # - borrowed_count: Integer, readonly=True, description='Number of times book was borrowed'
    # Hint: book_output = api.inherit('BookOutput', book_input, { ... })


    # In-memory storage
    books = []

    def find_book(book_id):
        """Find a book by ID."""
        for book in books:
            if book['id'] == book_id:
                return book
        return None

    # TODO 4: Create BookList Resource with comprehensive documentation
    @books_ns.route('/')
    class BookList(Resource):
        # TODO 4a: Document the GET endpoint
        # Add these decorators:
        # - @books_ns.doc('list_books') - Operation ID
        # - @books_ns.marshal_list_with(book_output) - Response format
        # - @books_ns.param('genre', 'Filter by genre', _in='query') - Query param docs
        # - @books_ns.param('available', 'Filter by availability (true/false)', _in='query')
        # - @books_ns.param('author', 'Filter by author name', _in='query')
        # - @books_ns.param('sort', 'Sort by field (title, author, year)', _in='query')
        # - @books_ns.param('limit', 'Maximum number of results', _in='query', type='integer')
        def get(self):
            """
            List all books with optional filtering and sorting.

            Returns a list of all books in the library. Supports filtering by genre,
            availability, and author. Results can be sorted and limited.

            TODO: Implement filtering and sorting
            """
            result = books.copy()

            # TODO 4b: Implement genre filter
            # Hint: genre = request.args.get('genre')
            # Hint: if genre: result = [b for b in result if b.get('genre') == genre]


            # TODO 4c: Implement available filter
            # Hint: available = request.args.get('available')
            # Hint: Convert to boolean and filter


            # TODO 4d: Implement author filter (case-insensitive)
            # Hint: Use .lower() for case-insensitive comparison


            # TODO 4e: Implement sorting
            # Hint: sort_by = request.args.get('sort', 'title')
            # Hint: Use sorted(result, key=lambda x: x.get(sort_by, ''))


            # TODO 4f: Implement limit
            # Hint: limit = request.args.get('limit', type=int)
            # Hint: if limit: result = result[:limit]


            return result

        # TODO 4g: Document the POST endpoint
        # Add these decorators:
        # - @books_ns.doc('create_book')
        # - @books_ns.expect(book_input, validate=True)
        # - @books_ns.marshal_with(book_output, code=201)
        # - @books_ns.response(201, 'Book successfully created')
        # - @books_ns.response(400, 'Validation error')
        # - @books_ns.response(409, 'Book with this ISBN already exists')
        def post(self):
            """
            Create a new book.

            Adds a new book to the library. ISBN must be unique.
            Automatically generates UUID, timestamps, and initializes borrowed_count.

            TODO: Implement book creation with validation
            """
            data = api.payload

            # TODO 4h: Check if ISBN already exists
            # Hint: for book in books:
            #     if book['isbn'] == data['isbn']:
            #         api.abort(409, f"Book with ISBN {data['isbn']} already exists")


            # TODO 4i: Create new book with generated fields
            # Hint: new_book = {
            #     'id': str(uuid.uuid4()),
            #     'created_at': datetime.now().isoformat(),
            #     'updated_at': datetime.now().isoformat(),
            #     'borrowed_count': 0,
            #     **data  # Spread operator to include all input fields
            # }


            # TODO 4j: Add to books list and return


    # TODO 5: Create Book Resource with full CRUD documentation
    @books_ns.route('/<string:id>')
    @books_ns.param('id', 'The book identifier (UUID)')
    @books_ns.response(404, 'Book not found')
    class Book(Resource):
        # TODO 5a: Document GET method
        # Add @books_ns.doc and @books_ns.marshal_with decorators
        def get(self, id):
            """
            Get a specific book by ID.

            Returns detailed information about a single book including
            all metadata and borrow statistics.

            TODO: Implement with error handling
            """
            # TODO: Find book and return 404 if not found


        # TODO 5b: Document PUT method
        # Add comprehensive documentation decorators
        def put(self, id):
            """
            Update a book's information.

            Updates all fields of an existing book. All fields must be provided
            (full replacement). Cannot change ID, timestamps, or borrowed_count.

            TODO: Implement update with validation
            """
            # TODO: Find book, validate, update, return


        # TODO 5c: Document DELETE method
        @books_ns.doc('delete_book')
        @books_ns.response(204, 'Book successfully deleted')
        def delete(self, id):
            """
            Delete a book from the library.

            Permanently removes a book from the system. This action cannot be undone.
            Returns 204 No Content on success.

            TODO: Implement deletion
            """
            # TODO: Find book, remove, return 204


    # TODO 6: Create Book Statistics Endpoint
    # This endpoint should return library statistics
    # @books_ns.route('/stats')
    # class BookStatistics(Resource):
    #     @books_ns.doc('book_statistics')
    #     def get(self):
    #         """
    #         Get library statistics.
    #
    #         Returns comprehensive statistics about the book library including:
    #         - Total number of books
    #         - Books by genre breakdown
    #         - Available vs borrowed books
    #         - Most popular books (by borrowed_count)
    #         """
    #         # TODO: Calculate and return statistics
    #         # Return structure:
    #         # {
    #         #     "total_books": 0,
    #         #     "available_books": 0,
    #         #     "borrowed_books": 0,
    #         #     "by_genre": {"fiction": 0, "non-fiction": 0, ...},
    #         #     "most_popular": [...]  # Top 5 most borrowed books
    #         # }


    # TODO 7: Create Search Endpoint
    # @books_ns.route('/search')
    # class BookSearch(Resource):
    #     @books_ns.doc('search_books')
    #     @books_ns.param('q', 'Search query (searches in title and author)', required=True)
    #     @books_ns.param('limit', 'Maximum results', type='integer', default=10)
    #     @books_ns.marshal_list_with(book_output)
    #     def get(self):
    #         """
    #         Search for books by title or author.
    #
    #         Performs case-insensitive search across book titles and author names.
    #         Returns matching books sorted by relevance.
    #         """
    #         # TODO: Implement search functionality


    api.add_namespace(books_ns, path='/books')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("Exercise 5: Advanced Swagger Documentation")
    print("="*60)
    print("Swagger UI: http://localhost:5000/swagger")
    print("\nLook for these documentation features:")
    print("  ✓ Detailed descriptions for every endpoint")
    print("  ✓ Example values in request models")
    print("  ✓ Query parameter documentation")
    print("  ✓ Response code documentation")
    print("  ✓ Field constraints and validation rules")
    print("\nYour Swagger docs should be self-explanatory!")
    print("="*60 + "\n")

    app.run(debug=True, port=5000)
