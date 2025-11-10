# 🎨 Whiteboard Diagrams for Chapter 2: RESTful APIs

## Purpose
These diagrams explain REST principles and API design patterns. Draw these during your live coding session to help students understand WHY we design APIs the way we do.

---

## Diagram 1: What is REST? (Opening - 5 min)

```
REST = REpresentational State Transfer

Breaking it down:
┌──────────────────┬────────────────────────────────┐
│ Representational │ Resources have representations │
│                  │ (JSON, XML, HTML)              │
├──────────────────┼────────────────────────────────┤
│ State            │ Current condition of resource  │
│                  │ (published, draft, archived)   │
├──────────────────┼────────────────────────────────┤
│ Transfer         │ Client and server exchange     │
│                  │ resource representations       │
└──────────────────┴────────────────────────────────┘

Simpler explanation:
REST is a set of rules for designing APIs so they are:
- Predictable  → If you know one endpoint, you can guess others
- Stateless    → Each request is independent
- Cacheable    → Responses can be saved for reuse
- Scalable     → Can handle millions of users
```

**What to say:**
> "Forget the fancy name. REST just means: design your API with predictable URLs, use HTTP methods correctly, and make each request independent. That's it!"

---

## Diagram 2: Resources vs Actions (Core Concept - 10 min)

```
❌ BAD (Action-based URLs):

GET  /getAllArticles           ← Verb in URL
POST /createNewArticle         ← Verb in URL
GET  /getArticleById?id=5      ← Verb in URL
POST /deleteArticle            ← Wrong method!
GET  /updateArticleStatus      ← GET shouldn't modify


✅ GOOD (Resource-based URLs):

GET    /articles               ← Noun (resource)
POST   /articles               ← Noun (resource)
GET    /articles/5             ← Noun (resource)
DELETE /articles/5             ← Proper method
PATCH  /articles/5             ← Proper method

The Rule:
┌────────────────────────────────────────────┐
│  URLs = NOUNS (resources)                  │
│  HTTP Methods = VERBS (actions)            │
└────────────────────────────────────────────┘

Examples of Resources (Nouns):
- /users
- /articles
- /comments
- /orders
- /products

NOT Resources (Verbs):
- /getUser        ← Use GET /users/:id
- /createOrder    ← Use POST /orders
- /deleteComment  ← Use DELETE /comments/:id
```

**What to say:**
> "RESTful APIs use nouns for URLs, verbs for HTTP methods. It's like grammar: 'Get article 5' not 'GetArticle5'. Clean, predictable, universal!"

---

## Diagram 3: HTTP Methods Deep Dive (Before coding - 10 min)

```
The 5 HTTP Methods:

┌──────────┬─────────────┬────────────┬─────────────┐
│ Method   │ Action      │ Idempotent │ Safe        │
├──────────┼─────────────┼────────────┼─────────────┤
│ GET      │ Read        │ Yes        │ Yes         │
│ POST     │ Create      │ No         │ No          │
│ PUT      │ Full Update │ Yes        │ No          │
│ PATCH    │ Partial Upd │ No*        │ No          │
│ DELETE   │ Remove      │ Yes        │ No          │
└──────────┴─────────────┴────────────┴─────────────┘

Safe = Doesn't modify data (read-only)
Idempotent = Same result if called multiple times

Examples:

GET /articles/5
- Call once: Get article 5
- Call 100 times: Still get article 5 (no change)
- Safe ✅ Idempotent ✅

POST /articles {"title": "Hello"}
- Call once: Creates article 6
- Call again: Creates article 7 (different!)
- Safe ❌ Idempotent ❌

PUT /articles/5 {"title": "Updated", "content": "..."}
- Call once: Article 5 updated
- Call again: Article 5 updated to same value
- Safe ❌ Idempotent ✅

DELETE /articles/5
- Call once: Article 5 deleted
- Call again: Still deleted (same state)
- Safe ❌ Idempotent ✅


PUT vs PATCH:
┌────────────────────────────────────────────────┐
│ PUT = Full replacement                         │
│ Must send ALL fields                           │
│                                                │
│ PUT /articles/5                                │
│ {                                              │
│   "title": "New Title",                        │
│   "content": "New Content",                    │
│   "author_id": 1,                              │
│   "category": "Tech",                          │
│   "published": true                            │
│ }                                              │
│ → Replaces entire article                     │
└────────────────────────────────────────────────┘

┌────────────────────────────────────────────────┐
│ PATCH = Partial update                         │
│ Send ONLY changed fields                       │
│                                                │
│ PATCH /articles/5                              │
│ {                                              │
│   "published": true                            │
│ }                                              │
│ → Updates only 'published' field               │
│ → Other fields unchanged                       │
└────────────────────────────────────────────────┘
```

**What to say:**
> "Idempotent means 'safe to retry'. If network fails, you can retry DELETE without fear of double-deleting. POST is NOT idempotent - retry creates duplicates!"

---

## Diagram 4: URL Structure & Nesting (Before coding - 8 min)

```
Resource Hierarchy:

┌─────────────────────────────────────────────────┐
│  Collection                                     │
│  /articles                                      │
│                                                 │
│    ├─ Individual Resource                       │
│    │  /articles/5                                │
│    │                                            │
│    └─ Nested Collection                         │
│       /articles/5/comments                      │
│                                                 │
│          └─ Nested Individual Resource          │
│             /articles/5/comments/12             │
└─────────────────────────────────────────────────┘

Real-world example:

Library System:
GET  /libraries                    All libraries
GET  /libraries/1                  Specific library
GET  /libraries/1/books            Books in library 1
GET  /libraries/1/books/42         Specific book
GET  /libraries/1/books/42/reviews Book reviews

Relationship shows ownership:
- Library 1 owns books
- Book 42 belongs to library 1
- Reviews belong to book 42


Nesting Rules:
┌────────────────────────────────────────────────┐
│ ✅ Good nesting (2-3 levels):                  │
│    /articles/5/comments                        │
│    /users/10/orders                            │
│    /organizations/3/teams/7/members            │
│                                                │
│ ❌ Bad nesting (too deep):                     │
│    /countries/1/states/2/cities/3/streets/4... │
│    → Just use query params instead:           │
│    /streets?city_id=3                          │
└────────────────────────────────────────────────┘
```

**What to say:**
> "Nesting shows ownership. '/articles/5/comments' says 'comments that belong to article 5'. But don't nest too deep - 2-3 levels max, then use query params!"

---

## Diagram 5: Query Parameters vs Path Parameters (During Step 18 - 8 min)

```
Two ways to pass data:

1. Path Parameters (Required, Part of URL structure):
┌──────────────────────────────────────────┐
│ /articles/5                              │
│           └─ ID is required              │
│                                          │
│ /users/john/posts                        │
│        └─ Username is required           │
└──────────────────────────────────────────┘

Use for:
✅ Required identifiers
✅ Part of resource hierarchy
✅ Core to the endpoint


2. Query Parameters (Optional, For filtering/sorting):
┌──────────────────────────────────────────────────┐
│ /articles?status=published&category=tech         │
│           └──────────┬────────────┬──────────┘   │
│              Optional filters                     │
│                                                   │
│ /articles?sort=date&order=desc&limit=10          │
│           └──────────┬──────────────────┘        │
│              Optional modifiers                   │
└──────────────────────────────────────────────────┘

Use for:
✅ Filtering (status=published)
✅ Sorting (sort=date, order=desc)
✅ Pagination (page=2, limit=20)
✅ Searching (q=python)
✅ Optional parameters


Examples:

GET /articles
→ All articles

GET /articles?status=published
→ Only published articles

GET /articles?status=published&category=tech
→ Published tech articles

GET /articles?author_id=5
→ Articles by author 5

GET /articles?search=python&sort=date&limit=10
→ Top 10 recent articles about Python


Common Query Parameter Patterns:
┌──────────────┬────────────────────────────────┐
│ Pattern      │ Example                        │
├──────────────┼────────────────────────────────┤
│ Filtering    │ ?status=active                 │
│              │ ?category=tech                 │
├──────────────┼────────────────────────────────┤
│ Sorting      │ ?sort=created_at               │
│              │ ?order=desc                    │
├──────────────┼────────────────────────────────┤
│ Pagination   │ ?page=2&limit=20               │
│              │ ?offset=40&limit=20            │
├──────────────┼────────────────────────────────┤
│ Search       │ ?q=python                      │
│              │ ?search=flask                  │
├──────────────┼────────────────────────────────┤
│ Fields       │ ?fields=id,title,author        │
│              │ (sparse fieldsets)             │
└──────────────┴────────────────────────────────┘
```

**What to say:**
> "Path parameters are like street addresses - required and specific. Query parameters are like search filters - optional and flexible. 'Show me the house at 123 Main St (path) with blue doors (query)'"

---

## Diagram 6: HTTP Status Codes for REST APIs (During Step 6 - 8 min)

```
Status Codes You MUST Know:

2xx Success:
┌────────┬──────────────────┬─────────────────────────┐
│ Code   │ Name             │ When to Use             │
├────────┼──────────────────┼─────────────────────────┤
│ 200    │ OK               │ GET, PUT, PATCH success │
│ 201    │ Created          │ POST success            │
│ 204    │ No Content       │ DELETE success          │
└────────┴──────────────────┴─────────────────────────┘

4xx Client Errors:
┌────────┬──────────────────┬─────────────────────────┐
│ 400    │ Bad Request      │ Invalid JSON, wrong fmt │
│ 404    │ Not Found        │ Resource doesn't exist  │
│ 409    │ Conflict         │ Duplicate (email, slug) │
│ 422    │ Unprocessable    │ Validation failed       │
└────────┴──────────────────┴─────────────────────────┘

5xx Server Errors:
┌────────┬──────────────────┬─────────────────────────┐
│ 500    │ Internal Error   │ Bug in your code        │
│ 503    │ Service Unavail  │ Server overloaded       │
└────────┴──────────────────┴─────────────────────────┘


Correct Usage Examples:

Create Article (Success):
POST /articles
Request: {"title": "Hello", "content": "..."}
Response: 201 Created
{
  "id": 5,
  "title": "Hello",
  "created_at": "2024-01-15T10:00:00"
}

Create Article (Duplicate):
POST /articles
Request: {"slug": "hello"}  ← slug already exists
Response: 409 Conflict
{
  "message": "Article with this slug already exists"
}

Get Article (Success):
GET /articles/5
Response: 200 OK
{"id": 5, "title": "..."}

Get Article (Not Found):
GET /articles/999
Response: 404 Not Found
{"message": "Article 999 not found"}

Delete Article (Success):
DELETE /articles/5
Response: 204 No Content
(empty body)

Update Article (Validation Error):
PATCH /articles/5
Request: {"published": "maybe"}  ← should be boolean
Response: 422 Unprocessable Entity
{
  "errors": {
    "published": "Must be true or false"
  }
}


Common Mistakes:
┌────────────────────────┬─────────────────────────┐
│ ❌ Wrong                │ ✅ Right                 │
├────────────────────────┼─────────────────────────┤
│ POST returns 200       │ POST returns 201        │
│ DELETE returns 200     │ DELETE returns 204      │
│ 404 with data          │ 404 with error message  │
│ 200 for failures       │ 4xx/5xx for failures    │
└────────────────────────┴─────────────────────────┘
```

**What to say:**
> "Status codes are a universal language. Every developer knows 404 means 'not found', 201 means 'created'. Use them correctly and your API is self-documenting!"

---

## Diagram 7: REST API Request/Response Structure (During Step 4 - 5 min)

```
Anatomy of a REST Request:

┌─────────────────────────────────────────────────────┐
│ Method: POST                                        │ ◄─ What action
│ URL: /api/v1/articles                               │ ◄─ Which resource
│                                                     │
│ Headers:                                            │
│   Content-Type: application/json                   │ ◄─ Data format
│   Accept: application/json                         │ ◄─ Expected response
│   Authorization: Bearer token123                   │ ◄─ Who you are
│                                                     │
│ Body:                                               │
│ {                                                   │
│   "title": "My Article",                           │ ◄─ Data payload
│   "content": "This is...",                         │
│   "category": "tech"                               │
│ }                                                   │
└─────────────────────────────────────────────────────┘


Anatomy of a REST Response:

┌─────────────────────────────────────────────────────┐
│ Status: 201 Created                                 │ ◄─ Success/failure
│                                                     │
│ Headers:                                            │
│   Content-Type: application/json                   │ ◄─ Response format
│   Location: /api/v1/articles/42                    │ ◄─ New resource URL
│   X-RateLimit-Remaining: 99                        │ ◄─ API metadata
│                                                     │
│ Body:                                               │
│ {                                                   │
│   "id": 42,                                        │
│   "title": "My Article",                           │ ◄─ Created resource
│   "content": "This is...",                         │
│   "category": "tech",                              │
│   "created_at": "2024-01-15T10:30:00Z",           │
│   "author": {                                      │
│     "id": 5,                                       │
│     "name": "John Doe"                             │
│   }                                                 │
│ }                                                   │
└─────────────────────────────────────────────────────┘


JSON Structure Best Practices:
┌────────────────────────────────────────────────────┐
│ Consistent naming:                                 │
│ ✅ snake_case:  created_at, user_id                │
│ ✅ camelCase:   createdAt, userId                  │
│ ❌ Mixed:       created_at, userId (inconsistent!) │
│                                                    │
│ Nested resources:                                  │
│ {                                                  │
│   "id": 5,                                         │
│   "title": "Article",                              │
│   "author": {          ◄─ Nested object           │
│     "id": 10,                                      │
│     "name": "John"                                 │
│   },                                               │
│   "comments": [        ◄─ Array of objects        │
│     {"id": 1, "text": "Great!"},                  │
│     {"id": 2, "text": "Thanks"}                   │
│   ]                                                │
│ }                                                  │
└────────────────────────────────────────────────────┘
```

**What to say:**
> "Think of HTTP requests as envelopes. Method is the stamp (mail type), URL is the address, headers are metadata, body is the letter inside. Responses work the same way!"

---

## Diagram 8: CRUD to HTTP Method Mapping (During Step 11 - 5 min)

```
CRUD = Create, Read, Update, Delete

Mapping to REST:

┌────────┬──────────────┬──────────────────────────┐
│ CRUD   │ HTTP Method  │ REST Endpoint            │
├────────┼──────────────┼──────────────────────────┤
│ Create │ POST         │ POST /articles           │
│        │              │ → Creates new article    │
├────────┼──────────────┼──────────────────────────┤
│ Read   │ GET          │ GET /articles (all)      │
│        │              │ GET /articles/5 (one)    │
├────────┼──────────────┼──────────────────────────┤
│ Update │ PUT / PATCH  │ PUT /articles/5 (full)   │
│        │              │ PATCH /articles/5 (part) │
├────────┼──────────────┼──────────────────────────┤
│ Delete │ DELETE       │ DELETE /articles/5       │
└────────┴──────────────┴──────────────────────────┘


Complete REST CRUD Example:

1. CREATE (POST):
   POST /articles
   Body: {"title": "New", "content": "..."}
   Response: 201, {"id": 5, "title": "New", ...}

2. READ ALL (GET):
   GET /articles
   Response: 200, [{"id": 1, ...}, {"id": 2, ...}]

3. READ ONE (GET):
   GET /articles/5
   Response: 200, {"id": 5, "title": "New", ...}

4. UPDATE (PUT):
   PUT /articles/5
   Body: {"title": "Updated", "content": "...", ...}
   Response: 200, {"id": 5, "title": "Updated", ...}

5. PARTIAL UPDATE (PATCH):
   PATCH /articles/5
   Body: {"title": "Changed"}
   Response: 200, {"id": 5, "title": "Changed", ...}

6. DELETE:
   DELETE /articles/5
   Response: 204, (empty body)

7. READ DELETED (404):
   GET /articles/5
   Response: 404, {"message": "Article not found"}


Database vs REST:
┌─────────────────┬──────────────────────────────┐
│ Database SQL    │ REST API                     │
├─────────────────┼──────────────────────────────┤
│ INSERT INTO     │ POST /resource               │
│ SELECT          │ GET /resource                │
│ UPDATE          │ PUT/PATCH /resource/:id      │
│ DELETE          │ DELETE /resource/:id         │
└─────────────────┴──────────────────────────────┘
```

**What to say:**
> "CRUD is what you do with data. REST is HOW you expose those operations over HTTP. Every database operation maps to an HTTP method!"

---

## Diagram 9: RESTful Resource Relationships (During Step 10 - 8 min)

```
Types of Relationships:

1. One-to-Many:
┌──────────────┐         ┌──────────────┐
│   Author     │───────┬─│   Article    │
│              │       ├─│              │
│ id: 5        │       ├─│ author_id: 5 │
│ name: John   │       └─│ author_id: 5 │
└──────────────┘         └──────────────┘
                          (multiple)

REST Endpoints:
GET /authors/5              → Get author
GET /authors/5/articles     → All author's articles
GET /articles?author_id=5   → Same thing (alternative)


2. Nested Resources (Belongs To):
┌──────────────┐         ┌──────────────┐
│   Article    │───────┬─│   Comment    │
│              │       ├─│              │
│ id: 10       │       ├─│ article_id:10│
│              │       └─│ article_id:10│
└──────────────┘         └──────────────┘

REST Endpoints:
GET /articles/10/comments          → Comments for article
POST /articles/10/comments         → Add comment to article
DELETE /articles/10/comments/3     → Delete specific comment


3. Many-to-Many:
┌──────────────┐    ┌────────────┐    ┌──────────────┐
│   Article    │◄───│ ArticleTag │───►│     Tag      │
│              │    │            │    │              │
│ id: 5        │    │ article: 5 │    │ id: 1        │
│              │    │ tag: 1     │    │ name: python │
└──────────────┘    └────────────┘    └──────────────┘

REST Endpoints:
GET /articles/5/tags           → Tags for article 5
POST /articles/5/tags          → Add tag to article
DELETE /articles/5/tags/1      → Remove tag from article

GET /tags/1/articles           → Articles with tag 1


Designing Nested Endpoints:

Level 1 (Collection):
/articles                      ← All articles

Level 2 (Individual):
/articles/5                    ← Specific article

Level 3 (Nested Collection):
/articles/5/comments           ← Comments for article 5

Level 4 (Nested Individual):
/articles/5/comments/12        ← Specific comment

⚠️ Don't go deeper than 3-4 levels!

Bad (too deep):
/countries/1/states/2/cities/3/streets/4/houses/5/residents

Good (use query params):
/residents?house_id=5
or
/houses/5/residents
```

**What to say:**
> "Relationships show ownership. '/articles/5/comments' screams 'these comments belong to article 5'. But keep it shallow - 3 levels max!"

---

## Diagram 10: Stateless Architecture (During opening - 5 min)

```
❌ Stateful (Bad):

Request 1:
Client: POST /login
        {"username": "john", "password": "..."}
Server: Session created! Session ID: abc123
        Stores: sessions['abc123'] = {user: 'john'}

Request 2:
Client: GET /profile
        (expects server remembers session abc123)
Server: Looks up sessions['abc123'] → finds user 'john'
        Returns john's profile

Problem:
- Server must remember every user
- Doesn't scale (what if 1M users?)
- Can't distribute across servers easily


✅ Stateless (Good):

Request 1:
Client: POST /login
        {"username": "john", "password": "..."}
Server: Generates JWT token
        Token contains: {user_id: 5, name: 'john'}
        Returns: {"token": "eyJhbGc..."}
        Server forgets everything!

Request 2:
Client: GET /profile
        Header: Authorization: Bearer eyJhbGc...
Server: Decodes token → user_id=5
        Looks up user 5 from database
        Returns profile
        Server still remembers nothing!

Benefits:
✅ Scales infinitely (any server can handle request)
✅ No memory overhead (no session storage)
✅ Works with load balancers
✅ True REST architecture


Analogy:
Stateful  = Calling restaurant: "Hi, this is John from earlier..."
            (expects them to remember you)

Stateless = Drive-thru: "I'd like a burger" every time
            (complete request, no memory needed)
```

**What to say:**
> "Stateless means each request contains EVERYTHING needed. Don't rely on server memory. This lets you scale to millions of users across hundreds of servers!"

---

## Diagram 11: Content Negotiation (Advanced - 3 min)

```
Same resource, different representations:

Request 1 (JSON):
GET /articles/5
Headers:
  Accept: application/json

Response:
{
  "id": 5,
  "title": "Hello World",
  "content": "..."
}


Request 2 (XML):
GET /articles/5
Headers:
  Accept: application/xml

Response:
<article>
  <id>5</id>
  <title>Hello World</title>
  <content>...</content>
</article>


Request 3 (HTML):
GET /articles/5
Headers:
  Accept: text/html

Response:
<html>
  <h1>Hello World</h1>
  <p>...</p>
</html>


Same Data, Different Format!

Content-Type Header:
┌──────────────────────────┬────────────────┐
│ Format                   │ Content-Type   │
├──────────────────────────┼────────────────┤
│ JSON                     │ application/json
│ XML                      │ application/xml
│ HTML                     │ text/html
│ Plain Text               │ text/plain
│ CSV                      │ text/csv
└──────────────────────────┴────────────────┘

Most APIs only support JSON (simplest!)
```

**What to say:**
> "Content negotiation lets clients request data in their preferred format. But 99% of modern APIs just use JSON - it's simple and universal!"

---

## Diagram 12: REST API Versioning Strategies (During Step 2 - 5 min)

```
Why Version?

You release API v1:
100 mobile apps use it ✅

You want to change response format:
Old: {"user_name": "John"}
New: {"user": {"name": "John"}}  ← Better structure

Problem: Changes break 100 existing apps! 💥

Solution: Versioning! Both old and new versions coexist.


Strategy 1: URL Path Versioning (Most Common)
┌─────────────────────────────────────────┐
│ /api/v1/articles  ← Old version         │
│ /api/v2/articles  ← New version         │
└─────────────────────────────────────────┘

Pros: ✅ Clear, ✅ Easy to route
Cons: ❌ Clutters URL


Strategy 2: Header Versioning
┌─────────────────────────────────────────┐
│ GET /api/articles                       │
│ Header: Accept: application/vnd.api+json; version=1
└─────────────────────────────────────────┘

Pros: ✅ Clean URLs
Cons: ❌ Harder to test, ❌ Less obvious


Strategy 3: Query Parameter
┌─────────────────────────────────────────┐
│ /api/articles?version=1                 │
└─────────────────────────────────────────┘

Pros: ✅ Flexible
Cons: ❌ Mixes data with versioning


We Use: URL Path (/api/v1)
- Most visible
- Easiest to understand
- Industry standard


Version Lifecycle:
┌────────────────────────────────────────────┐
│ v1 Released → Jan 2024                     │
│ ├─ 100 apps using                          │
│ │                                           │
│ v2 Released → Jun 2024                     │
│ ├─ New apps use v2                         │
│ ├─ Old apps still on v1 ✅                 │
│ │                                           │
│ v1 Deprecated → Dec 2024                   │
│ ├─ Warning: v1 will be removed             │
│ ├─ Give 6 months to migrate                │
│ │                                           │
│ v1 Sunset → Jun 2025                       │
│ └─ v1 stopped working                      │
│    Old apps must upgrade                   │
└────────────────────────────────────────────┘
```

**What to say:**
> "Versioning is like software releases - Windows 10 and 11 coexist. Old users stay on 10, new users get 11. Eventually Windows 10 support ends, forcing upgrades!"

---

## Diagram 13: Validation & Error Responses (During Step 11 - 5 min)

```
Request Validation Flow:

Client sends:
POST /articles
{
  "title": "",                 ← Empty (invalid)
  "published": "maybe"         ← Should be boolean
}
          │
          ▼
┌──────────────────────────┐
│ Flask-RESTX Validation   │
│                          │
│ 1. Check required fields │
│    ✅ title present      │
│    ✅ published present  │
│                          │
│ 2. Check types           │
│    ✅ title is string    │
│    ❌ published not bool │
│                          │
│ 3. Check constraints     │
│    ❌ title is empty     │
└──────────────────────────┘
          │
          ▼
Response: 400 Bad Request
{
  "errors": {
    "title": "This field is required and cannot be empty",
    "published": "Must be a boolean (true or false)"
  },
  "message": "Input validation failed"
}


Validation Levels:

Level 1: Type Validation (Automatic)
┌────────────────────────────────────────┐
│ fields.String  → Must be string        │
│ fields.Integer → Must be integer       │
│ fields.Boolean → Must be true/false    │
└────────────────────────────────────────┘

Level 2: Constraint Validation (Model)
┌────────────────────────────────────────┐
│ required=True    → Must be present     │
│ min_length=3     → String length       │
│ min=0, max=100   → Number range        │
│ enum=['a', 'b']  → Must be in list     │
└────────────────────────────────────────┘

Level 3: Business Validation (Your Code)
┌────────────────────────────────────────┐
│ if Article.query.filter_by(slug=...).first():
│     abort(409, "Slug already exists")  │
│                                        │
│ if author_id not in valid_authors:     │
│     abort(400, "Invalid author")       │
└────────────────────────────────────────┘


Error Response Format (Consistent!):
{
  "message": "Main error description",
  "errors": {
    "field1": "Specific error for field1",
    "field2": "Specific error for field2"
  },
  "code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**What to say:**
> "Validation is like airport security - check at multiple levels! Type check (is it a number?), constraint check (is it positive?), business check (does author exist?)"

---

## Quick Reference: When to Draw Each Diagram

| Time | Diagram | Topic |
|------|---------|-------|
| 0-5 min | #1, #2 | REST fundamentals |
| 5-15 min | #3, #4, #5 | HTTP methods & URLs |
| 15-20 min | #6, #7 | Status codes & structure |
| 20-30 min | #8, #9 | CRUD & relationships |
| 30-35 min | #10, #11 | Stateless & content types |
| 35-40 min | #12, #13 | Versioning & validation |

---

## Teaching Tips

1. **Compare to real APIs** - "Twitter API works exactly like this!"

2. **Show bad examples first** - Students learn by seeing mistakes

3. **Use real-world analogies** - Restaurant, library, drive-thru

4. **Draw incrementally** - Build diagrams step-by-step

5. **Color-code** - Client (blue), Server (green), Errors (red)

6. **Leave diagrams visible** - Students reference during coding

7. **Ask questions** - "Why is POST not idempotent?"

8. **Use student suggestions** - "What status code should we return?"

---

**Remember:** REST is about DESIGN, not technology. These patterns work in any language!
