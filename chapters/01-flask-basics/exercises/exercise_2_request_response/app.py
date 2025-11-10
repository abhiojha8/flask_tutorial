"""
Exercise 2 Solution: Request and Response Handling

This solution demonstrates:
- Accessing request data (query parameters, JSON body)
- Returning different response types
- Using proper HTTP status codes
- Filtering and searching data
"""

from flask import Flask, request, jsonify
from datetime import datetime

def create_app():
    """Create the Flask application."""
    app = Flask(__name__)

    # In-memory storage for items
    items = []

    # TODO 1: GET /items endpoint with filtering
    @app.route('/items', methods=['GET'])
    def get_items():
        """List all items with optional filtering."""
        # Get query parameters
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)

        # Start with all items
        result = items.copy()

        # Filter by category if provided
        if category:
            result = [item for item in result if item.get('category') == category]

        # Limit results if specified
        if limit:
            result = result[:limit]

        return jsonify(result), 200

    # TODO 2: POST /items endpoint
    @app.route('/items', methods=['POST'])
    def create_item():
        """Create a new item."""
        data = request.json

        # Validate that name is provided
        if not data or 'name' not in data:
            return jsonify({"error": "Name is required"}), 400

        # Create new item
        new_item = {
            'id': len(items) + 1,
            'name': data['name'],
            'category': data.get('category', 'uncategorized'),
            'price': data.get('price', 0.0),
            'created_at': datetime.now().isoformat()
        }

        items.append(new_item)
        return jsonify(new_item), 201

    # TODO 3: GET /items/<id> endpoint
    @app.route('/items/<int:id>', methods=['GET'])
    def get_item(id):
        """Get a specific item by ID."""
        # Find item by id
        item = None
        for i in items:
            if i['id'] == id:
                item = i
                break

        if not item:
            return jsonify({"error": "Item not found"}), 404

        return jsonify(item), 200

    # TODO 4: DELETE /items/<id> endpoint
    @app.route('/items/<int:id>', methods=['DELETE'])
    def delete_item(id):
        """Delete an item by ID."""
        # Find item
        item = None
        for i in items:
            if i['id'] == id:
                item = i
                break

        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Remove from list
        items.remove(item)
        return '', 204

    # TODO 5: GET /items/search endpoint
    @app.route('/items/search', methods=['GET'])
    def search_items():
        """Search for items by name."""
        search_term = request.args.get('q', '')

        if not search_term:
            return jsonify({"error": "Search query 'q' is required"}), 400

        # Search (case-insensitive)
        results = [
            item for item in items
            if search_term.lower() in item['name'].lower()
        ]

        return jsonify(results), 200

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 2 Solution: Request and Response Handling")
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
