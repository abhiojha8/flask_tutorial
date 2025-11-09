"""
Exercise 1: HTTP Methods Mastery - Library Management API

OBJECTIVE:
Master all HTTP methods by building a Library Management API with proper status codes.

WHAT YOU'LL BUILD:
- Books resource (all CRUD operations)
- Members resource (all CRUD operations)
- Borrowing records (create, return, history)

LEARNING GOALS:
- GET for retrieving resources
- POST for creating resources
- PUT for full updates (requires all fields)
- PATCH for partial updates (only some fields)
- DELETE for removing resources
- Proper status codes for each operation

TODO CHECKLIST:
[ ] Implement all Books endpoints (GET, POST, PUT, PATCH, DELETE)
[ ] Implement all Members endpoints (GET, POST, PUT, DELETE)
[ ] Implement Borrowing endpoints (GET, POST, PATCH for return)
[ ] PUT requires all fields, PATCH allows partial updates
[ ] Use proper status codes (200, 201, 204, 400, 404, 409)
[ ] Cannot borrow unavailable books (409 Conflict)
[ ] Cannot delete members with unreturned books
[ ] Test all endpoints in Swagger UI

HINTS:
- Use in-memory lists for storage: books, members, borrowings
- Generate IDs using len(list) + 1 or uuid
- For PUT: require all fields in request, return 400 if any missing
- For PATCH: accept partial fields, only update provided ones
- Check book availability before creating borrowing record
- Check for active borrowings before deleting member
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
        description='Exercise 1: Master HTTP Methods with a Library API',
        doc='/swagger'
    )

    # ============================================================================
    # DATA MODELS - Define the structure of our resources
    # ============================================================================

    # Books namespace
    books_ns = Namespace('books', description='Book operations')

    # Book model for Swagger documentation
    book_model = books_ns.model('Book', {
        'id': fields.Integer(readonly=True, description='Book unique identifier'),
        'isbn': fields.String(required=True, description='ISBN number'),
        'title': fields.String(required=True, description='Book title'),
        'author': fields.String(required=True, description='Book author'),
        'publication_year': fields.Integer(required=True, description='Year published'),
        'genre': fields.String(required=True, description='Book genre'),
        'available': fields.Boolean(description='Availability status')
    })

    # Members namespace
    members_ns = Namespace('members', description='Member operations')

    # Member model for Swagger documentation
    member_model = members_ns.model('Member', {
        'id': fields.Integer(readonly=True, description='Member unique identifier'),
        'name': fields.String(required=True, description='Member name'),
        'email': fields.String(required=True, description='Member email'),
        'membership_date': fields.String(description='Date joined'),
        'books_borrowed': fields.Integer(description='Number of books currently borrowed')
    })

    # Borrowings namespace
    borrowings_ns = Namespace('borrowings', description='Borrowing operations')

    # Borrowing model for Swagger documentation
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

    # Books storage
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

    # Members storage
    members = [
        {
            'id': 1,
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'membership_date': '2024-01-15',
            'books_borrowed': 0
        }
    ]

    # Borrowing records storage
    borrowings = []

    # ============================================================================
    # HELPER FUNCTIONS
    # ============================================================================

    def find_book_by_id(book_id):
        """Find a book by ID."""
        # TODO: Implement this helper function
        # HINT: Use list comprehension or a for loop to find book with matching id
        # HINT: Return the book dict if found, None if not found
        pass

    def find_member_by_id(member_id):
        """Find a member by ID."""
        # TODO: Implement this helper function
        # HINT: Similar to find_book_by_id but for members list
        pass

    def find_borrowing_by_id(borrowing_id):
        """Find a borrowing record by ID."""
        # TODO: Implement this helper function
        pass

    def is_isbn_duplicate(isbn, exclude_id=None):
        """Check if ISBN already exists (excluding a specific book ID)."""
        # TODO: Implement duplicate ISBN checking
        # HINT: Loop through books, check if isbn matches
        # HINT: If exclude_id is provided, skip that book (for updates)
        # HINT: Return True if duplicate found, False otherwise
        pass

    def is_email_duplicate(email, exclude_id=None):
        """Check if email already exists (excluding a specific member ID)."""
        # TODO: Implement duplicate email checking
        pass

    def get_active_borrowings_for_member(member_id):
        """Get all unreturned books for a member."""
        # TODO: Return list of borrowings where:
        # HINT: - member_id matches
        # HINT: - returned_date is None (not returned yet)
        pass

    # ============================================================================
    # BOOKS ENDPOINTS
    # ============================================================================

    @books_ns.route('/')
    class BookList(Resource):
        """Books collection endpoint."""

        @books_ns.doc('list_books')
        @books_ns.marshal_list_with(book_model)
        def get(self):
            """
            List all books.

            TODO: Implement this endpoint
            HINT: Return the books list
            HINT: Status code 200 (automatically returned by default)
            """
            # TODO: Implement GET /books
            pass

        @books_ns.doc('create_book')
        @books_ns.expect(book_model)
        @books_ns.marshal_with(book_model, code=201)
        def post(self):
            """
            Add a new book.

            TODO: Implement this endpoint
            STEPS:
            1. Get the request data using api.payload
            2. Validate required fields are present
            3. Check for duplicate ISBN (return 409 if duplicate)
            4. Generate new ID (use len(books) + 1)
            5. Set available to True by default
            6. Add book to books list
            7. Return the new book with status code 201

            HINT: Use is_isbn_duplicate() helper
            HINT: Use books_ns.abort(409, "ISBN already exists") for conflicts
            HINT: Use books_ns.abort(400, "Missing required field: X") for validation
            """
            # TODO: Implement POST /books
            pass

    @books_ns.route('/<int:id>')
    @books_ns.response(404, 'Book not found')
    @books_ns.param('id', 'The book identifier')
    class BookItem(Resource):
        """Single book endpoint."""

        @books_ns.doc('get_book')
        @books_ns.marshal_with(book_model)
        def get(self, id):
            """
            Get a book by ID.

            TODO: Implement this endpoint
            HINT: Use find_book_by_id() helper
            HINT: If not found, use books_ns.abort(404, 'Book not found')
            HINT: Return the book dict with status 200
            """
            # TODO: Implement GET /books/{id}
            pass

        @books_ns.doc('update_book_full')
        @books_ns.expect(book_model)
        @books_ns.marshal_with(book_model)
        def put(self, id):
            """
            Update entire book record (all fields required).

            TODO: Implement this endpoint
            STEPS:
            1. Find the book by ID (abort 404 if not found)
            2. Get request data
            3. Validate ALL required fields are present (isbn, title, author, publication_year, genre)
            4. Check if ISBN changed and is duplicate (abort 409 if duplicate)
            5. Update ALL fields of the book
            6. Return updated book with status 200

            KEY DIFFERENCE FROM PATCH:
            - PUT requires ALL fields
            - PATCH allows partial updates

            HINT: Required fields: isbn, title, author, publication_year, genre
            HINT: Keep the same ID
            HINT: Preserve 'available' status or update if provided
            """
            # TODO: Implement PUT /books/{id}
            pass

        @books_ns.doc('update_book_partial')
        @books_ns.expect(book_model)
        @books_ns.marshal_with(book_model)
        def patch(self, id):
            """
            Partially update book (only provided fields).

            TODO: Implement this endpoint
            STEPS:
            1. Find the book by ID (abort 404 if not found)
            2. Get request data
            3. If 'isbn' is being updated, check for duplicates
            4. Update ONLY the fields that were provided in the request
            5. Return updated book with status 200

            KEY DIFFERENCE FROM PUT:
            - PATCH allows updating only some fields
            - PUT requires all fields

            HINT: Use book.update(api.payload) to update only provided fields
            HINT: Or manually update each field if it exists in payload
            """
            # TODO: Implement PATCH /books/{id}
            pass

        @books_ns.doc('delete_book')
        @books_ns.response(204, 'Book deleted')
        def delete(self, id):
            """
            Delete a book.

            TODO: Implement this endpoint
            STEPS:
            1. Find the book by ID (abort 404 if not found)
            2. Remove the book from books list
            3. Return empty response with status code 204

            HINT: Use books.remove(book)
            HINT: Return ('', 204) for 204 No Content status
            """
            # TODO: Implement DELETE /books/{id}
            pass

    # ============================================================================
    # MEMBERS ENDPOINTS
    # ============================================================================

    @members_ns.route('/')
    class MemberList(Resource):
        """Members collection endpoint."""

        @members_ns.doc('list_members')
        @members_ns.marshal_list_with(member_model)
        def get(self):
            """
            List all members.

            TODO: Implement this endpoint
            """
            # TODO: Implement GET /members
            pass

        @members_ns.doc('create_member')
        @members_ns.expect(member_model)
        @members_ns.marshal_with(member_model, code=201)
        def post(self):
            """
            Register a new member.

            TODO: Implement this endpoint
            STEPS:
            1. Get request data
            2. Validate required fields (name, email)
            3. Check for duplicate email (abort 409 if exists)
            4. Generate new ID
            5. Set membership_date to today
            6. Set books_borrowed to 0
            7. Add to members list
            8. Return new member with status 201

            HINT: Use datetime.now().strftime('%Y-%m-%d') for today's date
            """
            # TODO: Implement POST /members
            pass

    @members_ns.route('/<int:id>')
    @members_ns.response(404, 'Member not found')
    @members_ns.param('id', 'The member identifier')
    class MemberItem(Resource):
        """Single member endpoint."""

        @members_ns.doc('get_member')
        @members_ns.marshal_with(member_model)
        def get(self, id):
            """
            Get a member by ID.

            TODO: Implement this endpoint
            """
            # TODO: Implement GET /members/{id}
            pass

        @members_ns.doc('update_member')
        @members_ns.expect(member_model)
        @members_ns.marshal_with(member_model)
        def put(self, id):
            """
            Update member information.

            TODO: Implement this endpoint
            HINT: Similar to PUT /books/{id}
            HINT: Require name and email
            HINT: Check for duplicate email if changed
            """
            # TODO: Implement PUT /members/{id}
            pass

        @members_ns.doc('delete_member')
        @members_ns.response(204, 'Member deleted')
        @members_ns.response(409, 'Cannot delete member with unreturned books')
        def delete(self, id):
            """
            Delete a member (only if no unreturned books).

            TODO: Implement this endpoint
            STEPS:
            1. Find member (abort 404 if not found)
            2. Check for active borrowings using get_active_borrowings_for_member()
            3. If active borrowings exist, abort 409 with message
            4. Remove member from list
            5. Return 204 No Content

            BUSINESS RULE: Cannot delete members who have unreturned books
            """
            # TODO: Implement DELETE /members/{id}
            pass

    # ============================================================================
    # BORROWING ENDPOINTS
    # ============================================================================

    @borrowings_ns.route('/')
    class BorrowingList(Resource):
        """Borrowing records collection."""

        @borrowings_ns.doc('list_borrowings')
        @borrowings_ns.marshal_list_with(borrowing_model)
        def get(self):
            """
            List all borrowing records.

            TODO: Implement this endpoint
            """
            # TODO: Implement GET /borrowings
            pass

        @borrowings_ns.doc('create_borrowing')
        @borrowings_ns.expect(borrowing_model)
        @borrowings_ns.marshal_with(borrowing_model, code=201)
        @borrowings_ns.response(409, 'Book not available')
        @borrowings_ns.response(404, 'Book or member not found')
        def post(self):
            """
            Borrow a book.

            TODO: Implement this endpoint
            STEPS:
            1. Get request data (needs book_id and member_id)
            2. Validate book exists (abort 404 if not)
            3. Validate member exists (abort 404 if not)
            4. Check if book is available (abort 409 if not available)
            5. Generate new borrowing ID
            6. Set borrowed_date to today
            7. Set due_date to 14 days from today
            8. Set returned_date to None
            9. Mark book as unavailable (available = False)
            10. Increment member's books_borrowed count
            11. Add borrowing to borrowings list
            12. Return borrowing with status 201

            BUSINESS RULE: Cannot borrow unavailable books

            HINT: Use datetime.now()
            HINT: Use (datetime.now() + timedelta(days=14)) for due date
            HINT: Format dates with .strftime('%Y-%m-%d')
            """
            # TODO: Implement POST /borrowings
            pass

    @borrowings_ns.route('/<int:id>')
    @borrowings_ns.response(404, 'Borrowing record not found')
    @borrowings_ns.param('id', 'The borrowing record identifier')
    class BorrowingItem(Resource):
        """Single borrowing record endpoint."""

        @borrowings_ns.doc('get_borrowing')
        @borrowings_ns.marshal_with(borrowing_model)
        def get(self, id):
            """
            Get a borrowing record by ID.

            TODO: Implement this endpoint
            """
            # TODO: Implement GET /borrowings/{id}
            pass

    @borrowings_ns.route('/<int:id>/return')
    @borrowings_ns.response(404, 'Borrowing record not found')
    @borrowings_ns.response(400, 'Book already returned')
    @borrowings_ns.param('id', 'The borrowing record identifier')
    class BorrowingReturn(Resource):
        """Return a borrowed book."""

        @borrowings_ns.doc('return_book')
        @borrowings_ns.marshal_with(borrowing_model)
        def patch(self, id):
            """
            Return a borrowed book.

            TODO: Implement this endpoint
            STEPS:
            1. Find borrowing record (abort 404 if not found)
            2. Check if already returned (abort 400 if returned_date is not None)
            3. Set returned_date to today
            4. Find the book and mark as available (available = True)
            5. Find the member and decrement books_borrowed count
            6. Return updated borrowing with status 200

            WHY PATCH?: We're partially updating the borrowing record (just the returned_date)

            HINT: Check if borrowing['returned_date'] is not None
            """
            # TODO: Implement PATCH /borrowings/{id}/return
            pass

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
    print("LIBRARY MANAGEMENT API - Exercise 1: HTTP Methods Mastery")
    print("="*70)
    print("📚 Learning Objectives:")
    print("  - Master all HTTP methods (GET, POST, PUT, PATCH, DELETE)")
    print("  - Understand proper status codes")
    print("  - Implement business logic validation")
    print("\n🎯 Your Tasks:")
    print("  1. Implement all TODO sections")
    print("  2. Test each endpoint in Swagger UI")
    print("  3. Verify proper status codes")
    print("  4. Test error cases (404, 409, 400)")
    print("\n🌐 Swagger UI: http://localhost:5000/swagger")
    print("="*70 + "\n")

    app.run(debug=True, port=5000)
