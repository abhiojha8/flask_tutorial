# Chapter 2: Exercises - RESTful API Design

## Overview
These exercises progressively build your understanding of RESTful API design, from basic HTTP methods to advanced concepts like nested resources and best practices.

---

## Exercise 1: HTTP Methods Mastery 📚

### Objective
Master all HTTP methods by building a Library Management API.

### What You'll Learn
- GET for retrieving resources
- POST for creating resources
- PUT for full updates
- PATCH for partial updates
- DELETE for removing resources
- Proper status codes for each operation

### Requirements
Build a Library API with three resources:

#### Resources
1. **Books**
   - Fields: id, isbn, title, author, publication_year, genre, available
   - All CRUD operations

2. **Members**
   - Fields: id, name, email, membership_date, books_borrowed
   - All CRUD operations

3. **Borrowing Records**
   - Fields: id, book_id, member_id, borrowed_date, due_date, returned_date
   - Create borrow record (POST)
   - Return book (PATCH to update returned_date)
   - List borrowing history (GET)

### API Endpoints to Implement

```
Books:
GET    /books           - List all books
GET    /books/{id}      - Get book details
POST   /books           - Add new book
PUT    /books/{id}      - Update entire book record
PATCH  /books/{id}      - Update specific fields
DELETE /books/{id}      - Remove book

Members:
GET    /members         - List all members
GET    /members/{id}    - Get member details
POST   /members         - Register new member
PUT    /members/{id}    - Update member info
DELETE /members/{id}    - Remove member

Borrowing:
GET    /borrowings              - List all borrowing records
GET    /borrowings/{id}         - Get specific record
POST   /borrowings              - Borrow a book
PATCH  /borrowings/{id}/return  - Return a book
```

### Success Criteria
- [ ] All HTTP methods implemented correctly
- [ ] PUT requires all fields, PATCH allows partial updates
- [ ] Proper status codes (200, 201, 204, 400, 404, 409)
- [ ] Cannot borrow unavailable books (409 Conflict)
- [ ] Cannot delete members with unreturned books
- [ ] Swagger UI documentation complete

### Test Scenarios
1. Create a book, update with PUT (all fields required)
2. Partial update with PATCH (only some fields)
3. Try to borrow unavailable book (should fail with 409)
4. Return a book successfully
5. Try to delete member with active borrowing (should fail)

---

## Exercise 2: Status Codes & Error Handling 🚨

### Objective
Implement proper HTTP status codes and meaningful error messages for an E-commerce API.

### What You'll Learn
- When to use each status code (200, 201, 204, 400, 404, 409, 422)
- Error response formats
- Input validation
- Business rule validation
- Meaningful error messages

### Requirements
Build a Product Catalog API with proper error handling:

#### Resources
1. **Products**
   - Fields: id, sku, name, description, price, stock_quantity, category

2. **Orders**
   - Fields: id, customer_email, items (list), total_amount, status

### Status Codes to Implement

| Code | When to Use | Example |
|------|-------------|---------|
| 200 | Successful GET, PUT, PATCH | Product retrieved |
| 201 | Successful POST | Product created |
| 204 | Successful DELETE | Product deleted |
| 400 | Invalid request data | Missing required field |
| 404 | Resource not found | Product ID doesn't exist |
| 409 | Business rule conflict | SKU already exists |
| 422 | Validation failed | Price must be positive |

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Product validation failed",
    "details": {
      "price": "Price must be greater than 0",
      "stock_quantity": "Stock cannot be negative"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v2/products"
  }
}
```

### Validation Rules
**Products:**
- SKU must be unique (409 if duplicate)
- Price must be > 0 (422 if invalid)
- Stock quantity must be >= 0 (422 if invalid)
- Name length: 3-200 characters (422 if invalid)
- Category must be from predefined list (422 if invalid)

**Orders:**
- All products must exist (404 if product not found)
- Sufficient stock available (409 if insufficient)
- Total amount must match calculated total (400 if mismatch)
- Customer email must be valid format (422 if invalid)

### API Endpoints
```
GET    /products
POST   /products
GET    /products/{id}
PUT    /products/{id}
DELETE /products/{id}

POST   /orders           - Create order (checks stock, deducts inventory)
GET    /orders/{id}
PATCH  /orders/{id}/cancel - Cancel order (restore stock)
```

### Success Criteria
- [ ] All status codes used appropriately
- [ ] Consistent error response format
- [ ] Helpful error messages
- [ ] Field-level validation errors
- [ ] Business logic validation
- [ ] Cannot create order with insufficient stock

### Test Scenarios
1. Create product with duplicate SKU → 409
2. Create product with negative price → 422
3. Get non-existent product → 404
4. Create order with insufficient stock → 409
5. Create order with invalid email → 422
6. Successfully create and cancel order → 201, 200

---

## Exercise 3: Query Parameters & Filtering 🔍

### Objective
Master query parameters for filtering, sorting, searching, and pagination.

### What You'll Learn
- Filtering by field values
- Search functionality
- Sorting (ascending/descending)
- Pagination
- Field selection
- Combining multiple query parameters

### Requirements
Build a Product Catalog API with advanced query capabilities.

#### Product Model
```python
{
    'id': '...',
    'name': 'Laptop',
    'description': '...',
    'price': 999.99,
    'category': 'Electronics',
    'brand': 'TechCorp',
    'stock': 50,
    'rating': 4.5,
    'tags': ['computer', 'portable'],
    'featured': True,
    'created_at': '...'
}
```

### Query Parameters to Implement

#### Filtering
```
GET /products?category=Electronics
GET /products?brand=TechCorp
GET /products?min_price=100&max_price=1000
GET /products?in_stock=true
GET /products?rating_gte=4.0
GET /products?featured=true
```

#### Searching
```
GET /products?search=laptop
GET /products?name_contains=laptop
GET /products?tags_contains=portable
```

#### Sorting
```
GET /products?sort=price              # Ascending
GET /products?sort=-price             # Descending (- prefix)
GET /products?sort=rating,-price      # Multiple fields
```

#### Pagination
```
GET /products?page=1&per_page=20
GET /products?limit=10&offset=20
```

#### Field Selection
```
GET /products?fields=id,name,price    # Only return specified fields
GET /products?exclude=description     # Exclude fields
```

#### Combining Parameters
```
GET /products?category=Electronics&min_price=500&sort=-rating&page=1&per_page=10
```

### Response Format with Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 156,
    "pages": 16,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "category": "Electronics",
    "min_price": 500
  }
}
```

### Success Criteria
- [ ] All filter types implemented
- [ ] Search works across multiple fields
- [ ] Sorting supports multiple fields
- [ ] Pagination includes metadata
- [ ] Can combine multiple query parameters
- [ ] Invalid query parameters return 400
- [ ] Empty results return [] not 404

### Test Scenarios
1. Filter by category and price range
2. Search in name and description
3. Sort by multiple fields
4. Paginate through results
5. Select specific fields only
6. Combine all features: filter + search + sort + paginate

---

## Exercise 4: Nested Resources 🏫

### Objective
Design and implement properly nested resources showing parent-child relationships.

### What You'll Learn
- Hierarchical resource design
- Parent resource validation
- Cascading operations
- URL structure for nested resources
- When to nest vs when to keep flat

### Requirements
Build a School Management API with multiple nesting levels.

#### Resource Hierarchy
```
Schools
  └── Classes
        └── Students
              └── Grades
```

### Data Models

**School**
```python
{
    'id': '...',
    'name': 'Lincoln High School',
    'address': '...',
    'principal': 'Dr. Smith',
    'student_count': 500
}
```

**Class**
```python
{
    'id': '...',
    'school_id': '...',
    'name': 'Grade 10A',
    'subject': 'Mathematics',
    'teacher': 'Mr. Johnson',
    'student_count': 30
}
```

**Student**
```python
{
    'id': '...',
    'class_id': '...',
    'school_id': '...',
    'name': 'Alice Wilson',
    'email': '...',
    'enrollment_date': '...',
    'gpa': 3.8
}
```

**Grade**
```python
{
    'id': '...',
    'student_id': '...',
    'subject': 'Math',
    'grade': 'A',
    'score': 95,
    'date': '...'
}
```

### API Endpoints

```
Schools:
GET    /schools
POST   /schools
GET    /schools/{school_id}
DELETE /schools/{school_id}

Classes (nested under schools):
GET    /schools/{school_id}/classes
POST   /schools/{school_id}/classes
GET    /schools/{school_id}/classes/{class_id}
PUT    /schools/{school_id}/classes/{class_id}
DELETE /schools/{school_id}/classes/{class_id}

Students (nested under classes):
GET    /schools/{school_id}/classes/{class_id}/students
POST   /schools/{school_id}/classes/{class_id}/students
GET    /schools/{school_id}/classes/{class_id}/students/{student_id}
DELETE /schools/{school_id}/classes/{class_id}/students/{student_id}

Grades (nested under students):
GET    /schools/{school_id}/classes/{class_id}/students/{student_id}/grades
POST   /schools/{school_id}/classes/{class_id}/students/{student_id}/grades

Alternative flat endpoints for convenience:
GET    /students/{student_id}              # Get student from any school/class
GET    /students/{student_id}/grades       # Get all grades for student
GET    /classes?school_id={id}            # All classes in a school
GET    /students?class_id={id}            # All students in a class
```

### Validation Rules
1. Cannot create class without valid school
2. Cannot create student without valid class
3. Deleting school deletes all classes and students (cascade)
4. Deleting class moves students to "unassigned" or deletes
5. Verify parent-child relationship in nested endpoints

### Success Criteria
- [ ] All nested endpoints work correctly
- [ ] Parent resource validation enforced
- [ ] Proper 404 when parent doesn't exist
- [ ] Cascading deletes implemented
- [ ] Alternative flat endpoints for convenience
- [ ] URL structure follows REST conventions
- [ ] Student count auto-updates

### Test Scenarios
1. Create school → class → student hierarchy
2. Try to create class with invalid school_id → 404
3. Get all students in a specific class
4. Delete school (verify cascade)
5. Use both nested and flat endpoints
6. Verify student counts update correctly

---

## Exercise 5: RESTful Best Practices 🏆

### Objective
Refactor a poorly designed API to follow REST principles and industry best practices.

### What You'll Learn
- REST conventions and anti-patterns
- URL design principles
- Resource naming
- HTTP method usage
- Response consistency

### The Bad API (Refactor This!)

```python
# ❌ Poor RESTful design
GET    /getAllUsers
POST   /createUser
GET    /getUserById?id=123
POST   /updateUserInfo
POST   /deleteUser?userId=123
GET    /user_search?name=john
POST   /user_activate
POST   /user_deactivate
GET    /fetchUserOrders?userId=123
POST   /placeNewOrder
GET    /getOrderStatus?orderId=456
POST   /cancelOrderNow
GET    /calculate_total?orderId=456
```

### Your Task
Redesign this API following REST principles:

#### Resources to Identify
1. Users
2. Orders
3. (Any others you identify)

#### Apply These Principles

**1. Resource-Based URLs**
```
❌ Bad:  /getAllUsers
✅ Good: /users
```

**2. HTTP Methods for Actions**
```
❌ Bad:  POST /createUser
✅ Good: POST /users
```

**3. Noun-Based URLs**
```
❌ Bad:  POST /user_activate
✅ Good: PATCH /users/{id}/activate
```

**4. Proper Nesting**
```
❌ Bad:  GET /fetchUserOrders?userId=123
✅ Good: GET /users/{id}/orders
```

**5. Idempotent Operations**
```
❌ Bad:  POST /deleteUser
✅ Good: DELETE /users/{id}
```

**6. Calculated Fields**
```
❌ Bad:  GET /calculate_total?orderId=456
✅ Good: Include in GET /orders/{id} response
```

### Deliverables

1. **Redesigned API Specification**
   - Document all endpoints
   - Proper HTTP methods
   - Resource-based URLs
   - Explain your design decisions

2. **Implementation**
   - Implement the refactored API
   - Include all CRUD operations
   - Proper status codes
   - Nested resources where appropriate

3. **Comparison Document**
   - List each old endpoint
   - Show the new equivalent
   - Explain why the new design is better

### Example Refactoring

```python
# Before
@app.route('/getAllUsers', methods=['GET'])
def get_all_users():
    return jsonify(users), 200

# After
@users_ns.route('/')
class UserList(Resource):
    @users_ns.doc('list_users')
    @users_ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        return users
```

### Success Criteria
- [ ] All endpoints follow REST conventions
- [ ] Resource-based URLs (nouns, not verbs)
- [ ] Proper HTTP method usage
- [ ] Consistent response format
- [ ] Nested resources implemented correctly
- [ ] No redundant endpoints
- [ ] Comprehensive Swagger documentation
- [ ] Written comparison of old vs new

### Additional Challenges
1. Add pagination to list endpoints
2. Add filtering and sorting
3. Implement HATEOAS (links to related resources)
4. Add API versioning
5. Include rate limiting headers

---

## 🎯 Exercise Tips

### General Guidelines
1. **Start with data models** - Define your resources first
2. **Use Swagger** - Test as you build
3. **Follow naming conventions** - Plural nouns for collections
4. **Status codes matter** - Use the right code for each scenario
5. **Validate early** - Check inputs before processing
6. **Document as you go** - Write docstrings for all endpoints

### Testing Strategy
1. Test the happy path first
2. Test error cases (404, 400, 409)
3. Test edge cases (empty lists, duplicates)
4. Test with Swagger UI
5. Test with curl commands
6. Verify response formats

### Common Mistakes to Avoid
- ❌ Using verbs in URLs (`/getUser`, `/createOrder`)
- ❌ Wrong HTTP methods (POST for reads, GET for updates)
- ❌ Returning 200 for everything
- ❌ Inconsistent response formats
- ❌ Missing validation
- ❌ Not checking parent resources in nested endpoints

---

## 📚 Resources

- [REST API Tutorial](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [API Design Best Practices](https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design)
- [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)

---

*Remember: Good API design is about being predictable and consistent. If someone knows REST principles, they should be able to guess your API structure!*