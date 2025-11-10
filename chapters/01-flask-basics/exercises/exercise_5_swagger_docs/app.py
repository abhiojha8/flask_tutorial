"""
Exercise 5 Solution: Advanced Swagger Documentation

This solution demonstrates:
- Comprehensive API documentation
- Examples in data models
- Query parameter documentation
- Response code documentation
- Statistics and search endpoints
"""

from flask import Flask, request
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime
import uuid

def create_app():
    """Create the Flask application."""
    app = Flask(__name__)

    # Create Api with comprehensive metadata
    api = Api(
        app,
        title='Book Library API',
        version='1.0',
        description='A comprehensive API for managing a book library with detailed documentation',
        doc='/swagger'
    )

    books_ns = Namespace('books', description='Book management operations')

    # Detailed book input model with examples
    book_input = api.model('BookInput', {
        'title': fields.String(
            required=True,
            description='Book title',
            example='The Great Gatsby'
        ),
        'author': fields.String(
            required=True,
            description='Book author',
            example='F. Scott Fitzgerald'
        ),
        'isbn': fields.String(
            required=True,
            description='ISBN-13 number',
            example='978-0743273565'
        ),
        'published_year': fields.Integer(
            required=True,
            description='Year of publication',
            min=1000,
            max=2024,
            example=1925
        ),
        'genre': fields.String(
            required=True,
            description='Book genre',
            enum=['fiction', 'non-fiction', 'sci-fi', 'mystery', 'romance'],
            example='fiction'
        ),
        'pages': fields.Integer(
            description='Number of pages',
            min=1,
            example=180
        ),
        'available': fields.Boolean(
            default=True,
            description='Whether book is available for borrowing'
        )
    })

    # Detailed book output model
    book_output = api.inherit('BookOutput', book_input, {
        'id': fields.String(
            readonly=True,
            description='Unique book identifier (UUID)'
        ),
        'created_at': fields.String(
            readonly=True,
            description='Book creation timestamp (ISO 8601)'
        ),
        'updated_at': fields.String(
            readonly=True,
            description='Last update timestamp (ISO 8601)'
        ),
        'borrowed_count': fields.Integer(
            readonly=True,
            description='Number of times book was borrowed',
            example=5
        )
    })

    # In-memory storage
    books = []

    def find_book(book_id):
        """Find a book by ID."""
        for book in books:
            if book['id'] == book_id:
                return book
        return None

    # BookList Resource with comprehensive documentation
    @books_ns.route('/')
    class BookList(Resource):
        @books_ns.doc('list_books')
        @books_ns.marshal_list_with(book_output)
        @books_ns.param('genre', 'Filter by genre', _in='query')
        @books_ns.param('available', 'Filter by availability (true/false)', _in='query')
        @books_ns.param('author', 'Filter by author name', _in='query')
        @books_ns.param('sort', 'Sort by field (title, author, year)', _in='query')
        @books_ns.param('limit', 'Maximum number of results', _in='query', type='integer')
        def get(self):
            """
            List all books with optional filtering and sorting.

            Returns a list of all books in the library. Supports filtering by genre,
            availability, and author. Results can be sorted and limited.
            """
            result = books.copy()

            # Filter by genre
            genre = request.args.get('genre')
            if genre:
                result = [b for b in result if b.get('genre') == genre]

            # Filter by available
            available = request.args.get('available')
            if available:
                available_bool = available.lower() == 'true'
                result = [b for b in result if b.get('available') == available_bool]

            # Filter by author (case-insensitive)
            author = request.args.get('author')
            if author:
                result = [b for b in result if author.lower() in b.get('author', '').lower()]

            # Sort
            sort_by = request.args.get('sort', 'title')
            if sort_by in ['title', 'author', 'published_year']:
                result = sorted(result, key=lambda x: x.get(sort_by, ''))

            # Limit
            limit = request.args.get('limit', type=int)
            if limit:
                result = result[:limit]

            return result

        @books_ns.doc('create_book')
        @books_ns.expect(book_input, validate=True)
        @books_ns.marshal_with(book_output, code=201)
        @books_ns.response(201, 'Book successfully created')
        @books_ns.response(400, 'Validation error')
        @books_ns.response(409, 'Book with this ISBN already exists')
        def post(self):
            """
            Create a new book.

            Adds a new book to the library. ISBN must be unique.
            Automatically generates UUID, timestamps, and initializes borrowed_count.
            """
            data = api.payload

            # Check if ISBN already exists
            for book in books:
                if book['isbn'] == data['isbn']:
                    api.abort(409, f"Book with ISBN {data['isbn']} already exists")

            # Create new book with generated fields
            now = datetime.now().isoformat()
            new_book = {
                'id': str(uuid.uuid4()),
                'created_at': now,
                'updated_at': now,
                'borrowed_count': 0,
                **data  # Include all input fields
            }

            books.append(new_book)
            return new_book, 201

    # Book Resource with full CRUD documentation
    @books_ns.route('/<string:id>')
    @books_ns.param('id', 'The book identifier (UUID)')
    @books_ns.response(404, 'Book not found')
    class Book(Resource):
        @books_ns.doc('get_book')
        @books_ns.marshal_with(book_output)
        def get(self, id):
            """
            Get a specific book by ID.

            Returns detailed information about a single book including
            all metadata and borrow statistics.
            """
            book = find_book(id)
            if not book:
                api.abort(404, f'Book {id} not found')
            return book

        @books_ns.doc('update_book')
        @books_ns.expect(book_input, validate=True)
        @books_ns.marshal_with(book_output)
        @books_ns.response(409, 'ISBN already exists for another book')
        def put(self, id):
            """
            Update a book's information.

            Updates all fields of an existing book. All fields must be provided
            (full replacement). Cannot change ID, timestamps, or borrowed_count.
            """
            book = find_book(id)
            if not book:
                api.abort(404, f'Book {id} not found')

            data = api.payload

            # Check if ISBN is being changed to an existing one
            if data['isbn'] != book['isbn']:
                for b in books:
                    if b['id'] != id and b['isbn'] == data['isbn']:
                        api.abort(409, f"ISBN {data['isbn']} already exists")

            # Update fields
            book.update({
                'title': data['title'],
                'author': data['author'],
                'isbn': data['isbn'],
                'published_year': data['published_year'],
                'genre': data['genre'],
                'pages': data.get('pages'),
                'available': data.get('available', True),
                'updated_at': datetime.now().isoformat()
            })

            return book

        @books_ns.doc('delete_book')
        @books_ns.response(204, 'Book successfully deleted')
        def delete(self, id):
            """
            Delete a book from the library.

            Permanently removes a book from the system. This action cannot be undone.
            Returns 204 No Content on success.
            """
            book = find_book(id)
            if not book:
                api.abort(404, f'Book {id} not found')

            books.remove(book)
            return '', 204

    # Book Statistics Endpoint
    @books_ns.route('/stats')
    class BookStatistics(Resource):
        @books_ns.doc('book_statistics')
        def get(self):
            """
            Get library statistics.

            Returns comprehensive statistics about the book library including:
            - Total number of books
            - Books by genre breakdown
            - Available vs borrowed books
            - Most popular books (by borrowed_count)
            """
            total = len(books)
            available = len([b for b in books if b.get('available', True)])
            borrowed = total - available

            # Count by genre
            by_genre = {}
            for book in books:
                genre = book.get('genre', 'unknown')
                by_genre[genre] = by_genre.get(genre, 0) + 1

            # Most popular books (top 5)
            most_popular = sorted(
                books,
                key=lambda x: x.get('borrowed_count', 0),
                reverse=True
            )[:5]

            return {
                'total_books': total,
                'available_books': available,
                'borrowed_books': borrowed,
                'by_genre': by_genre,
                'most_popular': [
                    {
                        'id': b['id'],
                        'title': b['title'],
                        'borrowed_count': b.get('borrowed_count', 0)
                    }
                    for b in most_popular
                ]
            }

    # Search Endpoint
    @books_ns.route('/search')
    class BookSearch(Resource):
        @books_ns.doc('search_books')
        @books_ns.param('q', 'Search query (searches in title and author)', required=True)
        @books_ns.param('limit', 'Maximum results', type='integer', default=10)
        @books_ns.marshal_list_with(book_output)
        def get(self):
            """
            Search for books by title or author.

            Performs case-insensitive search across book titles and author names.
            Returns matching books sorted by relevance.
            """
            query = request.args.get('q', '').lower()
            limit = request.args.get('limit', 10, type=int)

            if not query:
                api.abort(400, 'Search query "q" is required')

            # Search in title and author
            results = [
                book for book in books
                if query in book.get('title', '').lower()
                or query in book.get('author', '').lower()
            ]

            # Limit results
            return results[:limit]

    api.add_namespace(books_ns, path='/books')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("Exercise 5 Solution: Advanced Swagger Documentation")
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
