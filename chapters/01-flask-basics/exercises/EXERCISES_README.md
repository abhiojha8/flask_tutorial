# Chapter 1: Flask Basics - Exercises

## 🎯 Overview

These exercises are designed to reinforce the concepts from Chapter 1. Each exercise builds on the previous one, gradually introducing more complexity.

**Complete these exercises in order** - they're designed to build your skills progressively!

---

## 📚 Exercise Structure

Each exercise includes:
- **Starter code** with `TODO` comments
- **Clear learning objectives**
- **Step-by-step guidance** in comments
- **Testing instructions**

---

## 🚀 Exercises

### Exercise 1: Hello API (🟢 Beginner)
**File:** `exercise_1_hello_api/app.py`

**What You'll Learn:**
- Create a basic Flask application
- Define routes with `@app.route()`
- Return JSON responses
- Use URL parameters
- Use factory pattern

**Time:** 20-30 minutes

**Key Concepts:**
- Flask app creation
- GET endpoints
- JSON responses with `jsonify()`
- URL parameter capture `<name>`
- POST endpoints with request body

**Success Criteria:**
- ✅ GET `/hello` returns greeting
- ✅ GET `/hello/<name>` returns personalized greeting
- ✅ POST `/greet` accepts JSON and returns greeting with timestamp

---

### Exercise 2: Request and Response Handling (🟢 Beginner)
**File:** `exercise_2_request_response/app.py`

**What You'll Learn:**
- Access query parameters
- Handle JSON request body
- Return different HTTP status codes
- Filter and limit results
- Implement search functionality

**Time:** 30-45 minutes

**Key Concepts:**
- `request.args.get()` for query parameters
- `request.json` for JSON body
- List filtering with comprehensions
- Proper status codes (200, 201, 404, 204)
- CRUD operations basics

**Success Criteria:**
- ✅ GET `/items` with filtering by category and limit
- ✅ POST `/items` creates item with validation
- ✅ GET `/items/<id>` returns specific item or 404
- ✅ DELETE `/items/<id>` removes item and returns 204
- ✅ GET `/items/search?q=term` searches items

---

### Exercise 3: Input Validation and Flask-RESTX (🟡 Intermediate)
**File:** `exercise_3_validation/app.py`

**What You'll Learn:**
- Set up Flask-RESTX
- Define data models with `fields`
- Use automatic validation
- Generate Swagger documentation
- Use Resource classes

**Time:** 45-60 minutes

**Key Concepts:**
- `Api()` initialization
- `Namespace` for organization
- `api.model()` for data schemas
- `@expect()` for input validation
- `@marshal_with()` for output formatting
- Enum fields for restricted values
- Automatic Swagger UI generation

**Success Criteria:**
- ✅ Flask-RESTX API configured
- ✅ Product model with validation
- ✅ CRUD operations using Resource classes
- ✅ Swagger UI accessible at `/swagger`
- ✅ Automatic validation rejects invalid data

---

### Exercise 4: Error Handling and Status Codes (🟡 Intermediate)
**File:** `exercise_4_error_handling/app.py`

**What You'll Learn:**
- Handle different error scenarios
- Return appropriate HTTP status codes
- Use `api.abort()` for errors
- Validate business logic
- Create comprehensive error responses

**Time:** 45-60 minutes

**Key Concepts:**
- `api.abort()` for proper error responses
- Status code meanings (400, 404, 409)
- Duplicate detection (409 Conflict)
- Data validation (400 Bad Request)
- Resource not found (404 Not Found)
- Helper functions for code organization

**Error Scenarios to Handle:**
- Duplicate username (409)
- Invalid email format (400)
- Invalid age range (400)
- User not found (404)
- Updating to existing username (409)

**Success Criteria:**
- ✅ All error scenarios return correct status codes
- ✅ Error messages are clear and helpful
- ✅ Validation happens before data modification
- ✅ Swagger documents all possible responses

---

### Exercise 5: Advanced Swagger Documentation (🔴 Advanced)
**File:** `exercise_5_swagger_docs/app.py`

**What You'll Learn:**
- Write comprehensive API documentation
- Add examples to data models
- Document query parameters
- Use response decorators
- Create detailed endpoint descriptions

**Time:** 60-90 minutes

**Key Concepts:**
- Detailed model definitions with examples
- `@api.doc()` for endpoint documentation
- `@api.param()` for query parameter docs
- `@api.response()` for status code docs
- Field constraints (min, max, pattern)
- Enum fields with descriptions
- Statistics endpoints
- Search functionality

**Success Criteria:**
- ✅ Every endpoint has clear description
- ✅ All models have example values
- ✅ Query parameters are documented
- ✅ All possible responses documented
- ✅ Field validation rules are clear
- ✅ Statistics endpoint returns meaningful data
- ✅ Search functionality works correctly

---

## 🛠️ How to Complete Exercises

### Step 1: Read the Exercise File
Open the `app.py` file for the exercise. Read through all the TODO comments to understand what you need to implement.

### Step 2: Follow the TODOs
Complete each TODO in order. The TODOs are numbered and build on each other.

### Step 3: Test Your Code
Run the application:
```bash
cd exercise_X_name/
python app.py
```

### Step 4: Test Endpoints
Use one of these methods:
- **Swagger UI** (easiest!): Visit `http://localhost:5000/swagger`
- **curl**: `curl http://localhost:5000/endpoint`
- **Postman** or similar API testing tool

### Step 5: Verify Success Criteria
Make sure all success criteria are met before moving to the next exercise.

---

## 🧪 Testing Your Solutions

### Exercise 1: Hello API
```bash
# Test GET endpoint
curl http://localhost:5000/hello
# Expected: {"message": "Hello, Flask!"}

# Test personalized greeting
curl http://localhost:5000/hello/Alice
# Expected: {"message": "Hello, Alice!"}

# Test POST endpoint
curl -X POST http://localhost:5000/greet \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob"}'
# Expected: {"message": "Hello, Bob!", "timestamp": "..."}
```

### Exercise 2: Request and Response
```bash
# Create an item
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Python Book", "category": "books", "price": 29.99}'

# List items
curl http://localhost:5000/items

# Filter by category
curl "http://localhost:5000/items?category=books&limit=5"

# Search items
curl "http://localhost:5000/items/search?q=python"

# Delete item
curl -X DELETE http://localhost:5000/items/1
```

### Exercise 3-5: Use Swagger UI
For Exercises 3, 4, and 5, the **easiest way to test** is using Swagger UI:

1. Run the app: `python app.py`
2. Open browser: `http://localhost:5000/swagger`
3. Click on an endpoint
4. Click "Try it out"
5. Fill in the request data
6. Click "Execute"
7. See the response!

---

## 💡 Tips for Success

### General Tips
1. **Read all TODOs first** before coding
2. **Complete TODOs in order** - they build on each other
3. **Test frequently** - run the app after each TODO
4. **Use print statements** to debug
5. **Check the demo app** if you're stuck

### Common Mistakes to Avoid
- ❌ Skipping validation checks
- ❌ Forgetting to return status codes
- ❌ Not handling `None` cases
- ❌ Hardcoding values that should be dynamic
- ❌ Missing `return app` in factory pattern

### When You're Stuck
1. **Re-read the TODO comment** - hints are there!
2. **Check the demo app** - `../demo/app.py` has examples
3. **Look at the live coding guide** - step-by-step explanations
4. **Check Flask-RESTX docs** - https://flask-restx.readthedocs.io/
5. **Ask for help** - that's what we're here for!

---

## 🎯 Learning Path

```
Exercise 1         Exercise 2         Exercise 3
Basic Flask   →   Request/Response  →  Flask-RESTX
                                       & Validation
    ↓                                      ↓
Exercise 4                           Exercise 5
Error Handling  ←───────────────  Advanced Docs
```

**Recommended approach:**
1. Do Exercise 1 and 2 on Day 1 (after demo)
2. Do Exercise 3 on Day 1 evening or Day 2 morning
3. Do Exercise 4 and 5 after you're comfortable with Exercise 3

---

## 📊 Difficulty Progression

| Exercise | Difficulty | Time | Concepts |
|----------|-----------|------|----------|
| 1 | 🟢 Easy | 20-30 min | Basic Flask, routes, JSON |
| 2 | 🟢 Easy | 30-45 min | Query params, CRUD, status codes |
| 3 | 🟡 Medium | 45-60 min | Flask-RESTX, validation, Swagger |
| 4 | 🟡 Medium | 45-60 min | Error handling, business logic |
| 5 | 🔴 Hard | 60-90 min | Comprehensive documentation |

---

## ✅ Completion Checklist

Track your progress:

- [ ] Exercise 1: Hello API completed and tested
- [ ] Exercise 2: Request/Response completed and tested
- [ ] Exercise 3: Flask-RESTX validation working
- [ ] Exercise 4: All error scenarios handled correctly
- [ ] Exercise 5: Comprehensive Swagger docs generated

**Completed all 5?** Congratulations! You've mastered Flask Basics! 🎉

---

## 🚀 Next Steps

After completing these exercises:

1. **Review your code** - Can you make it cleaner?
2. **Push to GitHub** - Build your portfolio!
3. **Move to Chapter 2** - RESTful API Design
4. **Optional**: Try the advanced exercises in the original `README.md`

---

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-RESTX Documentation](https://flask-restx.readthedocs.io/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [JSON Specification](https://www.json.org/)

---

**Happy coding! Remember: The goal is learning, not perfection. Make mistakes, debug them, and grow! 💪**
