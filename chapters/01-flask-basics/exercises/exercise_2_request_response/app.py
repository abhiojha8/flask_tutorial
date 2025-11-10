"""
Exercise 2: Request and Response Handling

Learning Objectives:
- Access request data (query parameters, JSON body, headers)
- Return different response types
- Use proper HTTP status codes
- Handle different content types

TODO: Complete the marked sections!
"""

from flask import Flask, request, jsonify
from datetime import datetime

def create_app():
    """Create the Flask application."""
    app = Flask(__name__)

    # In-memory storage for items
    items = []

    # TODO 1: Create GET /items endpoint
    # This should:
    # - Accept query parameters: ?category=<category>&limit=<number>
    # - Filter items by category if provided
    # - Limit results if limit parameter provided
    # - Return list of items with 200 status code
    # Hint: Use request.args.get('category') to get query parameters


    # TODO 2: Create POST /items endpoint
    # This should:
    # - Accept JSON body with: {"name": "...", "category": "...", "price": 0.0}
    # - Validate that 'name' is provided (return 400 if missing)
    # - Add an 'id' (use len(items) + 1)
    # - Add 'created_at' timestamp
    # - Append to items list
    # - Return created item with 201 status code
    # Hint: Use request.json to get the JSON body
    # Hint: Use jsonify(item), 201 to return with status code


    # TODO 3: Create GET /items/<int:id> endpoint
    # This should:
    # - Find item by id
    # - Return 404 if not found
    # - Return item with 200 if found
    # Hint: Use list comprehension or loop to find item
    # Hint: return jsonify({"error": "Item not found"}), 404


    # TODO 4: Create DELETE /items/<int:id> endpoint
    # This should:
    # - Find and remove item by id
    # - Return 404 if not found
    # - Return 204 (no content) if successfully deleted
    # Hint: Use items.remove(item) to remove
    # Hint: return '', 204 for successful deletion with no content


    # TODO 5: Create GET /items/search endpoint
    # This should:
    # - Accept query parameter: ?q=<search_term>
    # - Search for items where search term appears in name (case-insensitive)
    # - Return list of matching items
    # Hint: Use .lower() for case-insensitive search
    # Hint: Use 'if search_term.lower() in item['name'].lower()'


    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 2: Request and Response Handling")
    print("="*50)
    print("Try these:")
    print("  GET  /items")
    print("  POST /items  (with JSON body)")
    print("  GET  /items/1")
    print("  GET  /items?category=books&limit=5")
    print("  GET  /items/search?q=python")
    print("  DELETE /items/1")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
