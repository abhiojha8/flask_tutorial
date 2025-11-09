"""
Exercise 1: HTTP Methods Mastery - Library Management API

SOLUTION - Complete implementation demonstrating all HTTP methods with proper status codes.

This solution shows:
- GET for retrieving resources
- POST for creating resources with 201 Created
- PUT for full updates (all fields required)
- PATCH for partial updates (only some fields)
- DELETE for removing resources with 204 No Content
- Proper validation and error handling
- Business logic (can't borrow unavailable books, can't delete members with active loans)
"""

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from datetime import datetime, timedelta

def create_app():
    """
    Create the Library Management API application.

    This API demonstrates all HTTP methods with proper status codes.
    """
    app = Flask(__name__)
    CORS(app)

    api = Api(
        app,
        version='1.0',
        title='Library Management API',
        description='Exercise 1 Solution: Master HTTP Methods with a Library API',
        doc='/swagger'
    )

    # ============================================================================
    # DATA MODELS
    # ============================================================================

    books_ns = Namespace('books', description='Book operations')

    book_model = books_ns.model('Book', {
        'id': fields.Integer(readonly=True, description='Book unique identifier'),
        'isbn': fields.String(required=True, description='ISBN number'),
        'title': fields.String(required=True, description='Book title'),
        'author': fields.String(required=True, description='Book author'),
        'publication_year': fields.Integer(required=True, description='Year published'),
        'genre': fields.String(required=True, description='Book genre'),
        'available': fields.Boolean(description='Availability status')
    })

    members_ns = Namespace('members', description='Member operations')

    member_model = members_ns.model('Member', {
        'id': fields.Integer(readonly=True, description='Member unique identifier'),
        'name': fields.String(required=True, description='Member name'),
        'email': fields.String(required=True, description='Member email'),
        'membership_date': fields.String(description='Date joined'),
        'books_borrowed': fields.Integer(description='Number of books currently borrowed')
    })

    borrowings_ns = Namespace('borrowings', description='Borrowing operations')

    borrowing_model = borrowings_ns.model('Borrowing', {
        'id': fields.Integer(readonly=True, description='Borrowing record ID'),
        'book_id': fields.Integer(required=True, description='ID of borrowed book'),
        'member_id': fields.Integer(required=True, description='ID of member'),
        'borrowed_date': fields.String(description='Date borrowed'),
        'due_date': fields.String(description='Due date'),
        'returned_date': fields.String(description='Date returned (null if not returned)')
    })

    # ============================================================================
    # IN-MEMORY DATA STORAGE
    # ============================================================================

    books = [
        {
            'id': 1,
            'isbn': '978-0-13-110362-7',
            'title': 'The C Programming Language',
            'author': 'Brian Kernighan and Dennis Ritchie',
            'publication_year': 1978,
            'genre': 'Programming',
            'available': True
        },
        {
            'id': 2,
            'isbn': '978-0-201-61622-4',
            'title': 'The Pragmatic Programmer',
            'author': 'Andrew Hunt and David Thomas',
            'publication_year': 1999,
            'genre': 'Programming',
            'available': True
        }
    ]

    members = [
        {
            'id': 1,
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'membership_date': '2024-01-15',
            'books_borrowed': 0
        }
    ]

    borrowings = []

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================

    def find_book_by_id(book_id):
        """Find a book by ID."""
        for book in books:
            if book['id'] == book_id:
                return book
        return None

    def find_member_by_id(member_id):
        """Find a member by ID."""
        for member in members:
            if member['id'] == member_id:
                return member
        return None

    def find_borrowing_by_id(borrowing_id):
        """Find a borrowing record by ID."""
        for borrowing in borrowings:
            if borrowing['id'] == borrowing_id:
                return borrowing
        return None

    def is_isbn_duplicate(isbn, exclude_id=None):
        """Check if ISBN already exists (excluding a specific book ID)."""
        for book in books:
            if book['isbn'] == isbn and book['id'] != exclude_id:
                return True
        return False

    def is_email_duplicate(email, exclude_id=None):
        """Check if email already exists (excluding a specific member ID)."""
        for member in members:
            if member['email'] == email and member['id'] != exclude_id:
                return True
        return False

    def get_active_borrowings_for_member(member_id):
        """Get all unreturned books for a member."""
        return [b for b in borrowings if b['member_id'] == member_id and b['returned_date'] is None]

    # ============================================================================
    # BOOKS ENDPOINTS
    # ============================================================================

    @books_ns.route('/')
    class BookList(Resource):
        """Books collection endpoint."""

        @books_ns.doc('list_books')
        @books_ns.marshal_list_with(book_model)
        def get(self):
            """List all books."""
            return books

        @books_ns.doc('create_book')
        @books_ns.expect(book_model)
        @books_ns.marshal_with(book_model, code=201)
        def post(self):
            """Add a new book."""
            data = books_ns.payload

            # Validate required fields
            required_fields = ['isbn', 'title', 'author', 'publication_year', 'genre']
            for field in required_fields:
                if field not in data:
                    books_ns.abort(400, f"Missing required field: {field}")

            # Check for duplicate ISBN
            if is_isbn_duplicate(data['isbn']):
                books_ns.abort(409, f"Book with ISBN {data['isbn']} already exists")

            # Generate new ID
            new_id = max([b['id'] for b in books]) + 1 if books else 1

            # Create new book
            new_book = {
                'id': new_id,
                'isbn': data['isbn'],
                'title': data['title'],
                'author': data['author'],
                'publication_year': data['publication_year'],
                'genre': data['genre'],
                'available': data.get('available', True)  # Default to True
            }

            books.append(new_book)
            return new_book, 201

    @books_ns.route('/<int:id>')
    @books_ns.response(404, 'Book not found')
    @books_ns.param('id', 'The book identifier')
    class BookItem(Resource):
        """Single book endpoint."""

        @books_ns.doc('get_book')
        @books_ns.marshal_with(book_model)
        def get(self, id):
            """Get a book by ID."""
            book = find_book_by_id(id)
            if not book:
                books_ns.abort(404, f"Book {id} not found")
            return book

        @books_ns.doc('update_book_full')
        @books_ns.expect(book_model)
        @books_ns.marshal_with(book_model)
        def put(self, id):
            """
            Update entire book record (all fields required).

            PUT requires ALL fields to be provided.
            """
            book = find_book_by_id(id)
            if not book:
                books_ns.abort(404, f"Book {id} not found")

            data = books_ns.payload

            # Validate ALL required fields are present (PUT requirement)
            required_fields = ['isbn', 'title', 'author', 'publication_year', 'genre']
            for field in required_fields:
                if field not in data:
                    books_ns.abort(400, f"PUT requires all fields. Missing: {field}")

            # Check for duplicate ISBN (if changed)
            if data['isbn'] != book['isbn'] and is_isbn_duplicate(data['isbn']):
                books_ns.abort(409, f"Book with ISBN {data['isbn']} already exists")

            # Update all fields
            book['isbn'] = data['isbn']
            book['title'] = data['title']
            book['author'] = data['author']
            book['publication_year'] = data['publication_year']
            book['genre'] = data['genre']
            book['available'] = data.get('available', book['available'])

            return book

        @books_ns.doc('update_book_partial')
        @books_ns.expect(book_model)
        @books_ns.marshal_with(book_model)
        def patch(self, id):
            """
            Partially update book (only provided fields).

            PATCH allows updating only specific fields.
            """
            book = find_book_by_id(id)
            if not book:
                books_ns.abort(404, f"Book {id} not found")

            data = books_ns.payload

            # Check for duplicate ISBN if being updated
            if 'isbn' in data and data['isbn'] != book['isbn']:
                if is_isbn_duplicate(data['isbn']):
                    books_ns.abort(409, f"Book with ISBN {data['isbn']} already exists")

            # Update only provided fields
            if 'isbn' in data:
                book['isbn'] = data['isbn']
            if 'title' in data:
                book['title'] = data['title']
            if 'author' in data:
                book['author'] = data['author']
            if 'publication_year' in data:
                book['publication_year'] = data['publication_year']
            if 'genre' in data:
                book['genre'] = data['genre']
            if 'available' in data:
                book['available'] = data['available']

            return book

        @books_ns.doc('delete_book')
        @books_ns.response(204, 'Book deleted')
        def delete(self, id):
            """Delete a book."""
            book = find_book_by_id(id)
            if not book:
                books_ns.abort(404, f"Book {id} not found")

            books.remove(book)
            return '', 204

    # ============================================================================
    # MEMBERS ENDPOINTS
    # ============================================================================

    @members_ns.route('/')
    class MemberList(Resource):
        """Members collection endpoint."""

        @members_ns.doc('list_members')
        @members_ns.marshal_list_with(member_model)
        def get(self):
            """List all members."""
            return members

        @members_ns.doc('create_member')
        @members_ns.expect(member_model)
        @members_ns.marshal_with(member_model, code=201)
        def post(self):
            """Register a new member."""
            data = members_ns.payload

            # Validate required fields
            if 'name' not in data:
                members_ns.abort(400, "Missing required field: name")
            if 'email' not in data:
                members_ns.abort(400, "Missing required field: email")

            # Check for duplicate email
            if is_email_duplicate(data['email']):
                members_ns.abort(409, f"Member with email {data['email']} already exists")

            # Generate new ID
            new_id = max([m['id'] for m in members]) + 1 if members else 1

            # Create new member
            new_member = {
                'id': new_id,
                'name': data['name'],
                'email': data['email'],
                'membership_date': datetime.now().strftime('%Y-%m-%d'),
                'books_borrowed': 0
            }

            members.append(new_member)
            return new_member, 201

    @members_ns.route('/<int:id>')
    @members_ns.response(404, 'Member not found')
    @members_ns.param('id', 'The member identifier')
    class MemberItem(Resource):
        """Single member endpoint."""

        @members_ns.doc('get_member')
        @members_ns.marshal_with(member_model)
        def get(self, id):
            """Get a member by ID."""
            member = find_member_by_id(id)
            if not member:
                members_ns.abort(404, f"Member {id} not found")
            return member

        @members_ns.doc('update_member')
        @members_ns.expect(member_model)
        @members_ns.marshal_with(member_model)
        def put(self, id):
            """Update member information."""
            member = find_member_by_id(id)
            if not member:
                members_ns.abort(404, f"Member {id} not found")

            data = members_ns.payload

            # Validate required fields for PUT
            if 'name' not in data:
                members_ns.abort(400, "PUT requires all fields. Missing: name")
            if 'email' not in data:
                members_ns.abort(400, "PUT requires all fields. Missing: email")

            # Check for duplicate email (if changed)
            if data['email'] != member['email'] and is_email_duplicate(data['email']):
                members_ns.abort(409, f"Member with email {data['email']} already exists")

            # Update fields
            member['name'] = data['name']
            member['email'] = data['email']

            return member

        @members_ns.doc('delete_member')
        @members_ns.response(204, 'Member deleted')
        @members_ns.response(409, 'Cannot delete member with unreturned books')
        def delete(self, id):
            """Delete a member (only if no unreturned books)."""
            member = find_member_by_id(id)
            if not member:
                members_ns.abort(404, f"Member {id} not found")

            # Check for active borrowings
            active_borrowings = get_active_borrowings_for_member(id)
            if active_borrowings:
                members_ns.abort(409, f"Cannot delete member with {len(active_borrowings)} unreturned book(s)")

            members.remove(member)
            return '', 204

    # ============================================================================
    # BORROWING ENDPOINTS
    # ============================================================================

    @borrowings_ns.route('/')
    class BorrowingList(Resource):
        """Borrowing records collection."""

        @borrowings_ns.doc('list_borrowings')
        @borrowings_ns.marshal_list_with(borrowing_model)
        def get(self):
            """List all borrowing records."""
            return borrowings

        @borrowings_ns.doc('create_borrowing')
        @borrowings_ns.expect(borrowing_model)
        @borrowings_ns.marshal_with(borrowing_model, code=201)
        @borrowings_ns.response(409, 'Book not available')
        @borrowings_ns.response(404, 'Book or member not found')
        def post(self):
            """Borrow a book."""
            data = borrowings_ns.payload

            # Validate required fields
            if 'book_id' not in data:
                borrowings_ns.abort(400, "Missing required field: book_id")
            if 'member_id' not in data:
                borrowings_ns.abort(400, "Missing required field: member_id")

            # Validate book exists
            book = find_book_by_id(data['book_id'])
            if not book:
                borrowings_ns.abort(404, f"Book {data['book_id']} not found")

            # Validate member exists
            member = find_member_by_id(data['member_id'])
            if not member:
                borrowings_ns.abort(404, f"Member {data['member_id']} not found")

            # Check if book is available
            if not book['available']:
                borrowings_ns.abort(409, f"Book '{book['title']}' is not available")

            # Generate new ID
            new_id = max([b['id'] for b in borrowings]) + 1 if borrowings else 1

            # Create borrowing record
            now = datetime.now()
            due_date = now + timedelta(days=14)

            new_borrowing = {
                'id': new_id,
                'book_id': data['book_id'],
                'member_id': data['member_id'],
                'borrowed_date': now.strftime('%Y-%m-%d'),
                'due_date': due_date.strftime('%Y-%m-%d'),
                'returned_date': None
            }

            # Update book availability
            book['available'] = False

            # Update member's borrowed count
            member['books_borrowed'] += 1

            borrowings.append(new_borrowing)
            return new_borrowing, 201

    @borrowings_ns.route('/<int:id>')
    @borrowings_ns.response(404, 'Borrowing record not found')
    @borrowings_ns.param('id', 'The borrowing record identifier')
    class BorrowingItem(Resource):
        """Single borrowing record endpoint."""

        @borrowings_ns.doc('get_borrowing')
        @borrowings_ns.marshal_with(borrowing_model)
        def get(self, id):
            """Get a borrowing record by ID."""
            borrowing = find_borrowing_by_id(id)
            if not borrowing:
                borrowings_ns.abort(404, f"Borrowing record {id} not found")
            return borrowing

    @borrowings_ns.route('/<int:id>/return')
    @borrowings_ns.response(404, 'Borrowing record not found')
    @borrowings_ns.response(400, 'Book already returned')
    @borrowings_ns.param('id', 'The borrowing record identifier')
    class BorrowingReturn(Resource):
        """Return a borrowed book."""

        @borrowings_ns.doc('return_book')
        @borrowings_ns.marshal_with(borrowing_model)
        def patch(self, id):
            """Return a borrowed book."""
            borrowing = find_borrowing_by_id(id)
            if not borrowing:
                borrowings_ns.abort(404, f"Borrowing record {id} not found")

            # Check if already returned
            if borrowing['returned_date'] is not None:
                borrowings_ns.abort(400, "Book has already been returned")

            # Update returned date
            borrowing['returned_date'] = datetime.now().strftime('%Y-%m-%d')

            # Mark book as available
            book = find_book_by_id(borrowing['book_id'])
            if book:
                book['available'] = True

            # Decrement member's borrowed count
            member = find_member_by_id(borrowing['member_id'])
            if member:
                member['books_borrowed'] -= 1

            return borrowing

    # ============================================================================
    # REGISTER NAMESPACES
    # ============================================================================

    api.add_namespace(books_ns, path='/books')
    api.add_namespace(members_ns, path='/members')
    api.add_namespace(borrowings_ns, path='/borrowings')

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*70)
    print("LIBRARY MANAGEMENT API - Exercise 1 SOLUTION")
    print("="*70)
    print("✅ All HTTP methods implemented:")
    print("  - GET for retrieving resources")
    print("  - POST for creating (201 Created)")
    print("  - PUT for full updates (all fields required)")
    print("  - PATCH for partial updates (some fields)")
    print("  - DELETE for removing (204 No Content)")
    print("\n✅ Business logic implemented:")
    print("  - Cannot borrow unavailable books (409 Conflict)")
    print("  - Cannot delete members with unreturned books")
    print("  - Duplicate ISBN/email prevention (409)")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
