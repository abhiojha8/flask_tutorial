# RESTful Blog API - Architecture Diagram

Visual overview of the complete application structure for Chapter 2.

---

## Application Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                       RESTful Blog API (v2.0)                       │
│                    http://localhost:5000/api/v2                     │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
            ┌───────▼────────┐           ┌────────▼────────┐
            │  Flask-RESTX   │           │   Swagger UI    │
            │   (API Core)   │           │  /swagger       │
            └───────┬────────┘           └─────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───▼───┐   ┌───▼───┐   ┌──▼────┐
    │Authors│   │Articles│   │Comments│
    │  NS   │   │   NS   │   │   NS   │
    └───────┘   └────────┘   └────────┘

NS = Namespace (Resource Collection)
```

---

## Complete Resource Hierarchy

```
API ROOT: /api/v2/
│
├── /authors/                           [Authors Collection]
│   ├── GET     → List all authors (200)
│   ├── POST    → Create author (201)
│   │
│   └── /{author_id}/                   [Single Author]
│       ├── GET     → Get author details (200)
│       ├── PUT     → Full update (200)
│       ├── PATCH   → Partial update (200)
│       ├── DELETE  → Delete author (204)
│       │
│       └── /articles/                  [Author's Articles]
│           └── GET → List author's articles (200)
│
├── /articles/                          [Articles Collection]
│   ├── GET     → List all articles (200)
│   │             ?published=true
│   │             ?category=Technology
│   │             ?author_id=123
│   │             ?tag=api
│   │             ?search=rest
│   │             ?sort=views
│   │             ?page=1&per_page=10
│   ├── POST    → Create article (201)
│   │
│   └── /{article_id}/                  [Single Article]
│       ├── GET     → Get article (200)
│       ├── PUT     → Full update (200)
│       ├── PATCH   → Partial update (200)
│       ├── DELETE  → Delete article (204)
│       │
│       ├── /comments/                  [Article's Comments - Nested Resource]
│       │   ├── GET  → List comments (200)
│       │   └── POST → Add comment (201)
│       │
│       ├── /publish/                   [Action Endpoint]
│       │   └── PUT  → Publish article (200)
│       │
│       └── /views/                     [Action Endpoint]
│           └── POST → Increment views (200)
│
└── /categories/                        [Categories Collection]
    └── GET     → List categories (200)
```

---

## Data Models & Relationships

```
┌──────────────────────────┐
│        Author            │
├──────────────────────────┤
│ id: string (UUID)        │
│ name: string*            │
│ email: string* (unique)  │
│ bio: string              │
│ article_count: int       │◄────────┐
│ created_at: datetime     │         │
└──────────────────────────┘         │ 1:N
              │                      │
              │ 1:N                  │
              │                      │
┌─────────────▼────────────┐         │
│        Article           │         │
├──────────────────────────┤         │
│ id: string (UUID)        │         │
│ title: string*           │         │
│ content: string*         │         │
│ slug: string             │         │
│ author_id: string*       │─────────┘
│ author: Author           │ (embedded)
│ category: string         │
│ tags: string[]           │
│ published: boolean       │
│ views: int               │
│ comment_count: int       │◄────────┐
│ created_at: datetime     │         │
│ updated_at: datetime     │         │ 1:N
└──────────────────────────┘         │
              │                      │
              │ 1:N                  │
              │                      │
┌─────────────▼────────────┐         │
│        Comment           │         │
├──────────────────────────┤         │
│ id: string (UUID)        │         │
│ article_id: string*      │─────────┘
│ author_name: string*     │
│ author_email: string*    │
│ content: string*         │
│ likes: int               │
│ created_at: datetime     │
└──────────────────────────┘

* = Required field
```

---

## HTTP Methods & Operations (CRUD Mapping)

```
┌─────────────┬──────────────┬─────────────┬────────────────┐
│ HTTP Method │   Operation  │ Status Code │     Action     │
├─────────────┼──────────────┼─────────────┼────────────────┤
│    GET      │     Read     │    200 OK   │   Retrieve     │
│             │              │             │   resource(s)  │
├─────────────┼──────────────┼─────────────┼────────────────┤
│    POST     │    Create    │ 201 Created │   Create new   │
│             │              │             │   resource     │
├─────────────┼──────────────┼─────────────┼────────────────┤
│    PUT      │  Full Update │    200 OK   │   Replace      │
│             │              │             │   entire       │
│             │              │             │   resource     │
├─────────────┼──────────────┼─────────────┼────────────────┤
│   PATCH     │Partial Update│    200 OK   │   Update some  │
│             │              │             │   fields       │
├─────────────┼──────────────┼─────────────┼────────────────┤
│   DELETE    │    Delete    │204 No Content│   Remove      │
│             │              │             │   resource     │
└─────────────┴──────────────┴─────────────┴────────────────┘
```

---

## Request/Response Flow

```
CLIENT REQUEST                      SERVER PROCESSING
═══════════════                    ══════════════════

1. POST /api/v2/articles            ┌─────────────────────┐
   Content-Type: application/json   │ 1. Route Matching   │
   {                                 │    articles_ns      │
     "title": "REST Guide",          └──────────┬──────────┘
     "content": "...",                          │
     "author_id": "abc123",          ┌──────────▼──────────┐
     "category": "Technology"        │ 2. Validation       │
   }                                 │    @expect(model)   │
           │                         │    Check required   │
           │                         └──────────┬──────────┘
           ▼                                    │
   ┌──────────────────┐              ┌──────────▼──────────┐
   │ Flask-RESTX      │              │ 3. Business Logic   │
   │ Receives Request │              │    - Verify author  │
   └──────────────────┘              │    - Create slug    │
                                     │    - Generate UUID  │
                                     └──────────┬──────────┘
                                                │
                                     ┌──────────▼──────────┐
                                     │ 4. Data Storage     │
                                     │    articles.append()│
                                     └──────────┬──────────┘
                                                │
2. RESPONSE                          ┌──────────▼──────────┐
   Status: 201 Created               │ 5. Response         │
   Location: /api/v2/articles/xyz    │    @marshal_with    │
   {                                 │    Format output    │
     "id": "xyz789",                 └─────────────────────┘
     "title": "REST Guide",
     "slug": "rest-guide",
     "author": {
       "id": "abc123",
       "name": "John Doe"
     },
     "views": 0,
     "comment_count": 0,
     "created_at": "2025-01-15T10:00:00"
   }
```

---

## Filtering & Pagination Architecture

```
GET /api/v2/articles?published=true&category=Technology&page=2&per_page=5
│
├─ Query Parameters Processing:
│  ┌────────────────────────────────────────────┐
│  │ 1. Extract Query Params                    │
│  │    published = request.args.get('published')│
│  │    category = request.args.get('category')  │
│  │    page = int(request.args.get('page', 1))  │
│  │    per_page = int(request.args.get('...'))  │
│  └────────────┬───────────────────────────────┘
│               │
│  ┌────────────▼───────────────────────────────┐
│  │ 2. Apply Filters                           │
│  │    filtered = [a for a in articles         │
│  │               if a.get('published') == True│
│  │               and a.get('category') == 'T..'│
│  └────────────┬───────────────────────────────┘
│               │
│  ┌────────────▼───────────────────────────────┐
│  │ 3. Calculate Pagination                    │
│  │    total = len(filtered)                   │
│  │    pages = (total + per_page - 1) // per_page│
│  │    start = (page - 1) * per_page           │
│  │    end = start + per_page                  │
│  │    items = filtered[start:end]             │
│  └────────────┬───────────────────────────────┘
│               │
└───────────────▼───────────────────────────────┐
                │ 4. Return Response             │
                │    {                           │
                │      "articles": [...],        │
                │      "pagination": {           │
                │        "page": 2,              │
                │        "per_page": 5,          │
                │        "total": 15,            │
                │        "pages": 3              │
                │      }                         │
                │    }                           │
                └────────────────────────────────┘
```

---

## Nested Resources Pattern

```
NESTED RESOURCE: Comments belong to Articles
═══════════════════════════════════════════

GET /api/v2/articles/123/comments
│
├─ Why Nested?
│  Comments don't exist independently
│  They always belong to an article
│  URL shows relationship clearly
│
└─ Flow:
   ┌──────────────────────────────────────┐
   │ 1. Extract article_id from URL       │
   │    article_id = "123"                │
   └────────────┬─────────────────────────┘
                │
   ┌────────────▼─────────────────────────┐
   │ 2. Verify article exists             │
   │    article = find_article(article_id)│
   │    if not article: return 404        │
   └────────────┬─────────────────────────┘
                │
   ┌────────────▼─────────────────────────┐
   │ 3. Filter comments by article        │
   │    article_comments = [              │
   │      c for c in comments             │
   │      if c['article_id'] == '123'     │
   │    ]                                 │
   └────────────┬─────────────────────────┘
                │
   ┌────────────▼─────────────────────────┐
   │ 4. Return filtered comments (200)    │
   └──────────────────────────────────────┘


POST /api/v2/articles/123/comments
{
  "author_name": "Jane",
  "author_email": "jane@example.com",
  "content": "Great article!"
}
│
└─ Flow:
   ┌──────────────────────────────────────┐
   │ 1. Validate article exists           │
   │    if not find_article('123'):       │
   │        return 404                    │
   └────────────┬─────────────────────────┘
                │
   ┌────────────▼─────────────────────────┐
   │ 2. Validate comment data             │
   │    @expect(comment_model)            │
   └────────────┬─────────────────────────┘
                │
   ┌────────────▼─────────────────────────┐
   │ 3. Auto-set article_id               │
   │    comment['article_id'] = '123'     │
   │    comment['id'] = str(uuid4())      │
   └────────────┬─────────────────────────┘
                │
   ┌────────────▼─────────────────────────┐
   │ 4. Store & increment comment count   │
   │    comments.append(comment)          │
   │    article['comment_count'] += 1     │
   └────────────┬─────────────────────────┘
                │
   ┌────────────▼─────────────────────────┐
   │ 5. Return created comment (201)      │
   │    Location: /articles/123/comments/x│
   └──────────────────────────────────────┘
```

---

## Status Code Decision Tree

```
                    ┌─────────────────┐
                    │ Request Arrives │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         ┌────▼────┐                   ┌────▼────┐
         │  GET    │                   │ POST    │
         └────┬────┘                   └────┬────┘
              │                             │
      ┌───────┴───────┐         ┌───────────┴───────────┐
      │               │         │                       │
  ┌───▼────┐    ┌────▼────┐  ┌─▼──────┐         ┌──────▼─────┐
  │Resource│    │Resource │  │Invalid │         │Valid       │
  │Exists? │    │List OK? │  │Data?   │         │Data?       │
  └───┬────┘    └────┬────┘  └────┬───┘         └──────┬─────┘
      │              │            │                    │
  ┌───▼───┐      ┌───▼───┐    ┌───▼───┐           ┌───▼───┐
  │200 OK │      │200 OK │    │400 Bad│           │201    │
  │+ data │      │+ list │    │Request│           │Created│
  └───────┘      └───────┘    └───────┘           └───┬───┘
                                                       │
      ┌────────────────────┐                      ┌────▼────┐
      │Resource Not Found  │                      │Location:│
      │404 Not Found       │                      │header   │
      └────────────────────┘                      └─────────┘

         ┌────────┐                    ┌────────┐
         │ PUT/   │                    │ DELETE │
         │ PATCH  │                    └────┬───┘
         └───┬────┘                         │
             │                         ┌────▼────┐
      ┌──────┴───────┐                │Resource │
      │              │                │Exists?  │
  ┌───▼────┐   ┌─────▼────┐          └────┬────┘
  │Valid   │   │Not Found │               │
  │Update? │   │404       │          ┌────▼────┐
  └───┬────┘   └──────────┘          │204 No   │
      │                              │Content  │
  ┌───▼────┐                         │(empty)  │
  │200 OK  │                         └─────────┘
  │+ data  │
  └────────┘
```

---

## Data Storage (In-Memory)

```
MEMORY STRUCTURE
════════════════

┌─────────────────────────────────────────┐
│         Application Memory              │
│                                         │
│  authors = [                            │
│    {                                    │
│      'id': 'uuid-1',                    │
│      'name': 'John Doe',                │
│      'email': 'john@example.com',       │
│      'bio': '...',                      │
│      'article_count': 5,                │
│      'created_at': datetime(...)        │
│    },                                   │
│    { ... }                              │
│  ]                                      │
│                                         │
│  articles = [                           │
│    {                                    │
│      'id': 'uuid-2',                    │
│      'title': 'REST API Guide',         │
│      'content': '...',                  │
│      'author_id': 'uuid-1',            │
│      'category': 'Technology',          │
│      'tags': ['api', 'rest'],           │
│      'published': True,                 │
│      'views': 150,                      │
│      'comment_count': 3,                │
│      'created_at': datetime(...),       │
│      'updated_at': datetime(...)        │
│    },                                   │
│    { ... }                              │
│  ]                                      │
│                                         │
│  comments = [                           │
│    {                                    │
│      'id': 'uuid-3',                    │
│      'article_id': 'uuid-2',            │
│      'author_name': 'Jane Smith',       │
│      'author_email': 'jane@ex.com',     │
│      'content': 'Great article!',       │
│      'likes': 5,                        │
│      'created_at': datetime(...)        │
│    },                                   │
│    { ... }                              │
│  ]                                      │
│                                         │
│  categories = [                         │
│    'Technology', 'Science',             │
│    'Business', 'Health', 'Sports'       │
│  ]                                      │
└─────────────────────────────────────────┘

NOTE: Data is lost on restart!
      This is for learning purposes.
      Production would use a database.
```

---

## Error Handling Flow

```
REQUEST ERROR HANDLING
══════════════════════

Request → Validation → Business Logic → Response
   │          │             │              │
   │          │             │              ▼
   │          │             │         ┌─────────┐
   │          │             │         │ Success │
   │          │             │         │ 2xx     │
   │          │             │         └─────────┘
   │          │             │
   │          │             ▼
   │          │        ┌──────────────────┐
   │          │        │ Resource Error   │
   │          │        │ 404 Not Found    │
   │          │        └──────────────────┘
   │          │
   │          ▼
   │     ┌─────────────────────────┐
   │     │ Validation Error        │
   │     │ 400 Bad Request         │
   │     │ {                       │
   │     │   "message": "...",     │
   │     │   "errors": {           │
   │     │     "title": ["..."],   │
   │     │     "content": ["..."]  │
   │     │   }                     │
   │     │ }                       │
   │     └─────────────────────────┘
   │
   ▼
┌──────────────────────────┐
│ Server Error             │
│ 500 Internal Server Error│
│ (Caught by Flask)        │
└──────────────────────────┘
```

---

## Key Design Patterns Used

### 1. **Resource-Oriented URLs**
```
✅ Good: /articles/123
❌ Bad:  /getArticle?id=123

✅ Good: /articles/123/comments
❌ Bad:  /getCommentsForArticle?article_id=123
```

### 2. **HTTP Method Semantics**
```
GET    → Safe, Idempotent (no side effects)
POST   → Not safe, Not idempotent (creates)
PUT    → Not safe, Idempotent (full replace)
PATCH  → Not safe, Not idempotent (partial)
DELETE → Not safe, Idempotent (removes)
```

### 3. **Namespaces for Organization**
```
articles_ns  → /articles/*
authors_ns   → /authors/*
comments_ns  → /articles/{id}/comments/*
```

### 4. **Model-Based Validation**
```python
@api.expect(article_model, validate=True)
```

### 5. **Marshalling (Output Formatting)**
```python
@api.marshal_with(article_output)
```

---

## Testing the Application

```
1. Start Server
   python app.py
   → http://localhost:5000/api/v2

2. Open Swagger
   http://localhost:5000/swagger

3. Test Flow:
   ┌─────────────────────────┐
   │ 1. Create Author (POST) │
   │    /authors/            │
   │    → Get author_id      │
   └───────────┬─────────────┘
               │
   ┌───────────▼─────────────┐
   │ 2. Create Article (POST)│
   │    /articles/           │
   │    → Use author_id      │
   │    → Get article_id     │
   └───────────┬─────────────┘
               │
   ┌───────────▼─────────────┐
   │ 3. Add Comment (POST)   │
   │    /articles/{id}/      │
   │    comments/            │
   └───────────┬─────────────┘
               │
   ┌───────────▼─────────────┐
   │ 4. List Articles (GET)  │
   │    /articles/           │
   │    ?published=true      │
   └───────────┬─────────────┘
               │
   ┌───────────▼─────────────┐
   │ 5. Update Article (PATCH│
   │    /articles/{id}       │
   └───────────┬─────────────┘
               │
   ┌───────────▼─────────────┐
   │ 6. Delete Article (DEL) │
   │    /articles/{id}       │
   │    → 204 No Content     │
   └─────────────────────────┘
```

---

## Use This Diagram During Teaching

**When to Show:**
1. **Start of Chapter 2** - Overview of what we'll build
2. **Before coding** - Explain resource relationships
3. **During namespaces** - Show organization structure
4. **When explaining CRUD** - Show HTTP method mapping
5. **During filtering** - Show query parameter flow
6. **End of chapter** - Review complete architecture

**Teaching Tips:**
- Draw the resource hierarchy on whiteboard first
- Show one endpoint at a time, build up complexity
- Use Swagger UI alongside diagram
- Point out REST principles as you code each part

---

## Architecture Principles Applied

✅ **Resource-Based** - Everything is a resource (articles, authors, comments)
✅ **Stateless** - Each request contains all needed information
✅ **Uniform Interface** - Consistent URL patterns and HTTP methods
✅ **Layered System** - Namespaces organize related endpoints
✅ **Cacheable** - GET requests return cacheable data
✅ **Client-Server** - Clear separation of concerns
✅ **Code on Demand** - Swagger UI provides interactive documentation
