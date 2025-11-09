"""
RESTful Blog API - Complete demonstration of REST principles
Teaches: Resources, HTTP methods, status codes, nested resources, filtering
"""

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
from datetime import datetime
import uuid
from werkzeug.exceptions import BadRequest

def create_app():
    """
    Create a RESTful Blog API demonstrating all REST principles.

    This API showcases:
    - Proper resource design (articles, authors, comments)
    - All HTTP methods (GET, POST, PUT, PATCH, DELETE)
    - Correct status codes
    - Nested resources
    - Query parameters for filtering and pagination
    - Error handling
    """
    app = Flask(__name__)

    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Configuration
    app.config['RESTX_VALIDATE'] = True
    app.config['RESTX_MASK_SWAGGER'] = False
    app.config['ERROR_404_HELP'] = False

    # Initialize Flask-RESTX with better documentation
    api = Api(
        app,
        version='2.0',
        title='RESTful Blog API',
        description='''
        A complete blog API demonstrating REST principles:
        - Resources: Articles, Authors, Comments, Categories
        - HTTP Methods: GET (read), POST (create), PUT (update), PATCH (partial update), DELETE (remove)
        - Status Codes: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found
        - Nested Resources: Articles have comments
        - Query Parameters: Filtering, sorting, pagination
        ''',
        doc='/swagger',
        prefix='/api/v2'
    )

    # In-memory data storage
    articles = []
    authors = []
    comments = []
    categories = ['Technology', 'Science', 'Business', 'Health', 'Sports']

    # Create namespaces (resource collections)
    articles_ns = api.namespace('articles', description='Article operations')
    authors_ns = api.namespace('authors', description='Author operations')
    comments_ns = api.namespace('articles', description='Comment operations')
    categories_ns = api.namespace('categories', description='Category operations')

    # Define models for validation and documentation

    # Author model
    author_model = api.model('Author', {
        'name': fields.String(required=True, description='Author name', example='John Doe'),
        'email': fields.String(required=True, description='Author email', example='john@example.com'),
        'bio': fields.String(description='Author biography', example='Tech writer and blogger')
    })

    author_output = api.inherit('AuthorOutput', author_model, {
        'id': fields.String(readonly=True, description='Author ID'),
        'article_count': fields.Integer(readonly=True, description='Number of articles written'),
        'created_at': fields.DateTime(readonly=True)
    })

    # Article model
    article_model = api.model('Article', {
        'title': fields.String(required=True, min_length=5, max_length=200,
                              description='Article title', example='Understanding REST APIs'),
        'content': fields.String(required=True, min_length=50,
                               description='Article content', example='REST is an architectural style...'),
        'author_id': fields.String(required=True, description='Author ID'),
        'category': fields.String(enum=categories, description='Article category'),
        'tags': fields.List(fields.String, description='Article tags', example=['api', 'rest', 'flask']),
        'published': fields.Boolean(default=False, description='Publication status')
    })

    article_output = api.inherit('ArticleOutput', article_model, {
        'id': fields.String(readonly=True),
        'slug': fields.String(readonly=True, description='URL-friendly title'),
        'views': fields.Integer(readonly=True, default=0),
        'comment_count': fields.Integer(readonly=True),
        'created_at': fields.DateTime(readonly=True),
        'updated_at': fields.DateTime(readonly=True),
        'author': fields.Nested(author_output, readonly=True)
    })

    # Partial update model (for PATCH)
    article_patch = api.model('ArticlePatch', {
        'title': fields.String(min_length=5, max_length=200),
        'content': fields.String(min_length=50),
        'category': fields.String(enum=categories),
        'tags': fields.List(fields.String),
        'published': fields.Boolean()
    })

    # Comment model
    comment_model = api.model('Comment', {
        'author_name': fields.String(required=True, description='Commenter name', example='Jane Smith'),
        'author_email': fields.String(required=True, description='Commenter email'),
        'content': fields.String(required=True, min_length=10, description='Comment content')
    })

    comment_output = api.inherit('CommentOutput', comment_model, {
        'id': fields.String(readonly=True),
        'article_id': fields.String(readonly=True),
        'created_at': fields.DateTime(readonly=True),
        'likes': fields.Integer(readonly=True, default=0)
    })

    # Pagination model
    pagination_model = api.model('Pagination', {
        'page': fields.Integer(description='Current page'),
        'per_page': fields.Integer(description='Items per page'),
        'total': fields.Integer(description='Total items'),
        'pages': fields.Integer(description='Total pages')
    })

    # Helper functions
    def find_article(article_id):
        """Find article by ID"""
        return next((a for a in articles if a['id'] == article_id), None)

    def find_author(author_id):
        """Find author by ID"""
        return next((a for a in authors if a['id'] == author_id), None)

    def get_article_comments(article_id):
        """Get all comments for an article"""
        return [c for c in comments if c['article_id'] == article_id]

    def create_slug(title):
        """Create URL-friendly slug from title"""
        return '-'.join(title.lower().split())[:50]

    def paginate(items, page=1, per_page=10):
        """Paginate a list of items"""
        total = len(items)
        pages = (total + per_page - 1) // per_page
        start = (page - 1) * per_page
        end = start + per_page

        return {
            'items': items[start:end],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages
            }
        }

    # Author endpoints
    @authors_ns.route('/')
    class AuthorList(Resource):
        @authors_ns.doc('list_authors')
        @authors_ns.marshal_list_with(author_output)
        def get(self):
            """
            List all authors

            This endpoint demonstrates:
            - GET method for retrieving resources
            - 200 OK status code
            """
            return authors

        @authors_ns.doc('create_author')
        @authors_ns.expect(author_model, validate=True)
        @authors_ns.marshal_with(author_output, code=201)
        @authors_ns.response(201, 'Author created successfully')
        @authors_ns.response(400, 'Validation error')
        def post(self):
            """
            Create a new author

            This endpoint demonstrates:
            - POST method for creating resources
            - 201 Created status code with Location header
            - Request body validation
            """
            data = api.payload

            # Check for duplicate email
            if any(a['email'] == data['email'] for a in authors):
                api.abort(400, f"Author with email {data['email']} already exists")

            author = {
                'id': str(uuid.uuid4()),
                'name': data['name'],
                'email': data['email'],
                'bio': data.get('bio', ''),
                'article_count': 0,
                'created_at': datetime.utcnow().isoformat()
            }
            authors.append(author)

            return author, 201, {'Location': f'/api/v2/authors/{author["id"]}'}

    @authors_ns.route('/<string:author_id>')
    @authors_ns.param('author_id', 'The author identifier')
    class Author(Resource):
        @authors_ns.doc('get_author')
        @authors_ns.marshal_with(author_output)
        @authors_ns.response(404, 'Author not found')
        def get(self, author_id):
            """
            Get author by ID

            This endpoint demonstrates:
            - GET method for single resource
            - Path parameters
            - 404 Not Found for missing resources
            """
            author = find_author(author_id)
            if not author:
                api.abort(404, f"Author {author_id} not found")

            # Calculate article count
            author['article_count'] = len([a for a in articles if a['author_id'] == author_id])
            return author

        @authors_ns.doc('delete_author')
        @authors_ns.response(204, 'Author deleted')
        @authors_ns.response(404, 'Author not found')
        @authors_ns.response(409, 'Author has articles')
        def delete(self, author_id):
            """
            Delete an author

            This endpoint demonstrates:
            - DELETE method
            - 204 No Content for successful deletion
            - 409 Conflict for business rule violations
            """
            author = find_author(author_id)
            if not author:
                api.abort(404, f"Author {author_id} not found")

            # Check if author has articles
            if any(a['author_id'] == author_id for a in articles):
                api.abort(409, "Cannot delete author with existing articles")

            authors.remove(author)
            return '', 204

    # Article endpoints
    @articles_ns.route('/')
    class ArticleList(Resource):
        @articles_ns.doc('list_articles')
        @articles_ns.param('page', 'Page number', type=int, default=1)
        @articles_ns.param('per_page', 'Items per page', type=int, default=10)
        @articles_ns.param('category', 'Filter by category', enum=categories)
        @articles_ns.param('author_id', 'Filter by author')
        @articles_ns.param('published', 'Filter by publication status', type=bool)
        @articles_ns.param('sort', 'Sort by field', enum=['created_at', 'updated_at', 'views', 'title'])
        @articles_ns.param('order', 'Sort order', enum=['asc', 'desc'], default='desc')
        @articles_ns.param('search', 'Search in title and content')
        def get(self):
            """
            List articles with filtering, sorting, and pagination

            This endpoint demonstrates:
            - Query parameters for filtering
            - Pagination
            - Sorting
            - Search functionality
            """
            # Start with all articles
            result = articles.copy()

            # Filtering
            category = request.args.get('category')
            if category:
                result = [a for a in result if a.get('category') == category]

            author_id = request.args.get('author_id')
            if author_id:
                result = [a for a in result if a['author_id'] == author_id]

            published = request.args.get('published')
            if published is not None:
                published = published.lower() == 'true'
                result = [a for a in result if a['published'] == published]

            # Search
            search = request.args.get('search')
            if search:
                search = search.lower()
                result = [a for a in result
                         if search in a['title'].lower() or search in a['content'].lower()]

            # Sorting
            sort_field = request.args.get('sort', 'created_at')
            sort_order = request.args.get('order', 'desc')
            reverse = sort_order == 'desc'

            if sort_field in ['created_at', 'updated_at', 'views', 'title']:
                result.sort(key=lambda x: x.get(sort_field, ''), reverse=reverse)

            # Add author info and comment count
            for article in result:
                article['author'] = find_author(article['author_id'])
                article['comment_count'] = len(get_article_comments(article['id']))

            # Pagination
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))

            response = paginate(result, page, per_page)

            return response

        @articles_ns.doc('create_article')
        @articles_ns.expect(article_model, validate=True)
        @articles_ns.marshal_with(article_output, code=201)
        @articles_ns.response(201, 'Article created')
        @articles_ns.response(400, 'Validation error')
        @articles_ns.response(404, 'Author not found')
        def post(self):
            """
            Create a new article

            This endpoint demonstrates:
            - POST for resource creation
            - Foreign key validation (author must exist)
            - Auto-generated fields (slug, timestamps)
            """
            data = api.payload

            # Validate author exists
            author = find_author(data['author_id'])
            if not author:
                api.abort(404, f"Author {data['author_id']} not found")

            article = {
                'id': str(uuid.uuid4()),
                'title': data['title'],
                'slug': create_slug(data['title']),
                'content': data['content'],
                'author_id': data['author_id'],
                'author': author,
                'category': data.get('category'),
                'tags': data.get('tags', []),
                'published': data.get('published', False),
                'views': 0,
                'comment_count': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            articles.append(article)

            return article, 201, {'Location': f'/api/v2/articles/{article["id"]}'}

    @articles_ns.route('/<string:article_id>')
    @articles_ns.param('article_id', 'The article identifier')
    class Article(Resource):
        @articles_ns.doc('get_article')
        @articles_ns.marshal_with(article_output)
        @articles_ns.response(404, 'Article not found')
        def get(self, article_id):
            """
            Get article by ID

            This endpoint demonstrates:
            - Single resource retrieval
            - Incrementing view counter (side effect)
            - Including related data (author, comments)
            """
            article = find_article(article_id)
            if not article:
                api.abort(404, f"Article {article_id} not found")

            # Increment views
            article['views'] = article.get('views', 0) + 1

            # Add related data
            article['author'] = find_author(article['author_id'])
            article['comment_count'] = len(get_article_comments(article_id))

            return article

        @articles_ns.doc('update_article')
        @articles_ns.expect(article_model, validate=True)
        @articles_ns.marshal_with(article_output)
        @articles_ns.response(200, 'Article updated')
        @articles_ns.response(404, 'Article not found')
        def put(self, article_id):
            """
            Update entire article (full replacement)

            This endpoint demonstrates:
            - PUT for full resource replacement
            - All fields required
            - Updated timestamp tracking
            """
            article = find_article(article_id)
            if not article:
                api.abort(404, f"Article {article_id} not found")

            data = api.payload

            # Validate author exists
            author = find_author(data['author_id'])
            if not author:
                api.abort(404, f"Author {data['author_id']} not found")

            # Full replacement (keeping only system fields)
            article.update({
                'title': data['title'],
                'slug': create_slug(data['title']),
                'content': data['content'],
                'author_id': data['author_id'],
                'author': author,
                'category': data.get('category'),
                'tags': data.get('tags', []),
                'published': data.get('published', False),
                'updated_at': datetime.utcnow().isoformat()
            })

            return article

        @articles_ns.doc('patch_article')
        @articles_ns.expect(article_patch, validate=True)
        @articles_ns.marshal_with(article_output)
        @articles_ns.response(200, 'Article updated')
        @articles_ns.response(404, 'Article not found')
        def patch(self, article_id):
            """
            Partially update article

            This endpoint demonstrates:
            - PATCH for partial updates
            - Only provided fields are updated
            - Difference from PUT method
            """
            article = find_article(article_id)
            if not article:
                api.abort(404, f"Article {article_id} not found")

            data = api.payload

            # Update only provided fields
            if 'title' in data:
                article['title'] = data['title']
                article['slug'] = create_slug(data['title'])

            if 'content' in data:
                article['content'] = data['content']

            if 'category' in data:
                article['category'] = data['category']

            if 'tags' in data:
                article['tags'] = data['tags']

            if 'published' in data:
                article['published'] = data['published']

            article['updated_at'] = datetime.utcnow().isoformat()

            # Refresh related data
            article['author'] = find_author(article['author_id'])
            article['comment_count'] = len(get_article_comments(article_id))

            return article

        @articles_ns.doc('delete_article')
        @articles_ns.response(204, 'Article deleted')
        @articles_ns.response(404, 'Article not found')
        def delete(self, article_id):
            """
            Delete an article

            This endpoint demonstrates:
            - DELETE method
            - Cascading deletion (removes comments too)
            - 204 No Content response
            """
            article = find_article(article_id)
            if not article:
                api.abort(404, f"Article {article_id} not found")

            # Delete all comments for this article (cascade)
            global comments
            comments = [c for c in comments if c['article_id'] != article_id]

            # Delete the article
            articles.remove(article)

            return '', 204

    # Nested resource: Comments under articles
    @comments_ns.route('/<string:article_id>/comments')
    @comments_ns.param('article_id', 'The article identifier')
    class ArticleCommentList(Resource):
        @comments_ns.doc('list_article_comments')
        @comments_ns.marshal_list_with(comment_output)
        @comments_ns.response(404, 'Article not found')
        def get(self, article_id):
            """
            List all comments for an article

            This endpoint demonstrates:
            - Nested resources (comments belong to articles)
            - Hierarchical URL structure
            """
            article = find_article(article_id)
            if not article:
                api.abort(404, f"Article {article_id} not found")

            return get_article_comments(article_id)

        @comments_ns.doc('create_comment')
        @comments_ns.expect(comment_model, validate=True)
        @comments_ns.marshal_with(comment_output, code=201)
        @comments_ns.response(201, 'Comment created')
        @comments_ns.response(404, 'Article not found')
        def post(self, article_id):
            """
            Add a comment to an article

            This endpoint demonstrates:
            - Creating nested resources
            - Parent resource validation
            """
            article = find_article(article_id)
            if not article:
                api.abort(404, f"Article {article_id} not found")

            data = api.payload
            comment = {
                'id': str(uuid.uuid4()),
                'article_id': article_id,
                'author_name': data['author_name'],
                'author_email': data['author_email'],
                'content': data['content'],
                'likes': 0,
                'created_at': datetime.utcnow().isoformat()
            }
            comments.append(comment)

            # Update article comment count
            article['comment_count'] = len(get_article_comments(article_id))

            return comment, 201

    @comments_ns.route('/<string:article_id>/comments/<string:comment_id>')
    @comments_ns.param('article_id', 'The article identifier')
    @comments_ns.param('comment_id', 'The comment identifier')
    class ArticleComment(Resource):
        @comments_ns.doc('delete_comment')
        @comments_ns.response(204, 'Comment deleted')
        @comments_ns.response(404, 'Comment not found')
        def delete(self, article_id, comment_id):
            """
            Delete a comment

            This endpoint demonstrates:
            - Deleting nested resources
            - Verifying parent-child relationship
            """
            comment = next((c for c in comments
                          if c['id'] == comment_id and c['article_id'] == article_id), None)

            if not comment:
                api.abort(404, f"Comment {comment_id} not found for article {article_id}")

            comments.remove(comment)

            # Update article comment count
            article = find_article(article_id)
            if article:
                article['comment_count'] = len(get_article_comments(article_id))

            return '', 204

    # Category endpoints (read-only resource)
    @categories_ns.route('/')
    class CategoryList(Resource):
        @categories_ns.doc('list_categories')
        def get(self):
            """
            List all categories

            This endpoint demonstrates:
            - Read-only resources (no POST, PUT, DELETE)
            - Static resource lists
            """
            return {
                'categories': categories,
                'total': len(categories)
            }

    # Statistics endpoint
    @articles_ns.route('/stats')
    class ArticleStats(Resource):
        @articles_ns.doc('article_statistics')
        def get(self):
            """
            Get article statistics

            This endpoint demonstrates:
            - Aggregate endpoints
            - Computed resources
            """
            published_count = len([a for a in articles if a['published']])
            draft_count = len(articles) - published_count

            total_views = sum(a.get('views', 0) for a in articles)
            total_comments = len(comments)

            articles_by_category = {}
            for cat in categories:
                articles_by_category[cat] = len([a for a in articles
                                                if a.get('category') == cat])

            return {
                'total_articles': len(articles),
                'published': published_count,
                'drafts': draft_count,
                'total_views': total_views,
                'total_comments': total_comments,
                'total_authors': len(authors),
                'articles_by_category': articles_by_category,
                'average_views': total_views / len(articles) if articles else 0
            }

    # Popular articles endpoint
    @articles_ns.route('/popular')
    class PopularArticles(Resource):
        @articles_ns.doc('popular_articles')
        @articles_ns.param('limit', 'Number of articles to return', type=int, default=5)
        @articles_ns.marshal_list_with(article_output)
        def get(self):
            """
            Get most popular articles by views

            This endpoint demonstrates:
            - Custom resource collections
            - Computed rankings
            """
            limit = int(request.args.get('limit', 5))

            # Sort by views
            sorted_articles = sorted(articles,
                                   key=lambda x: x.get('views', 0),
                                   reverse=True)

            # Add related data
            for article in sorted_articles[:limit]:
                article['author'] = find_author(article['author_id'])
                article['comment_count'] = len(get_article_comments(article['id']))

            return sorted_articles[:limit]

    # Register all namespaces
    api.add_namespace(articles_ns)
    api.add_namespace(authors_ns)
    api.add_namespace(categories_ns)

    # Seed some initial data for testing
    def seed_data():
        """Add some initial data for demonstration"""
        # Create authors
        author1 = {
            'id': str(uuid.uuid4()),
            'name': 'Alice Johnson',
            'email': 'alice@blog.com',
            'bio': 'Tech enthusiast and API expert',
            'article_count': 0,
            'created_at': datetime.utcnow().isoformat()
        }
        author2 = {
            'id': str(uuid.uuid4()),
            'name': 'Bob Smith',
            'email': 'bob@blog.com',
            'bio': 'Software architect',
            'article_count': 0,
            'created_at': datetime.utcnow().isoformat()
        }
        authors.extend([author1, author2])

        # Create articles
        article1 = {
            'id': str(uuid.uuid4()),
            'title': 'Understanding RESTful APIs',
            'slug': 'understanding-restful-apis',
            'content': 'REST (Representational State Transfer) is an architectural style that defines a set of constraints for creating web services. RESTful APIs use HTTP methods explicitly and follow REST principles.',
            'author_id': author1['id'],
            'author': author1,
            'category': 'Technology',
            'tags': ['REST', 'API', 'Web Services'],
            'published': True,
            'views': 42,
            'comment_count': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        articles.append(article1)

    # Seed data on startup
    seed_data()

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    print("="*60)
    print("RESTful Blog API - Chapter 2: Understanding REST")
    print("="*60)
    print("Swagger UI: http://localhost:5000/swagger")
    print("")
    print("Key concepts demonstrated:")
    print("- Resources: Articles, Authors, Comments, Categories")
    print("- HTTP Methods: GET, POST, PUT, PATCH, DELETE")
    print("- Status Codes: 200, 201, 204, 400, 404, 409")
    print("- Nested Resources: /articles/{id}/comments")
    print("- Query Parameters: ?page=1&category=Technology")
    print("- Error Handling: Proper HTTP status codes")
    print("="*60)

    app.run(debug=True, host='0.0.0.0', port=5000)