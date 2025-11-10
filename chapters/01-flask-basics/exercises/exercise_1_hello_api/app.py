"""
Exercise 1 Solution: Hello API - Your First Flask Application

This solution demonstrates:
- Creating a basic Flask application
- Defining routes with different HTTP methods
- Returning JSON responses
- Using factory pattern
"""

from flask import Flask, jsonify, request
from datetime import datetime

def create_app():
    """Create and configure the Flask application."""
    # Step 1: Create Flask instance
    app = Flask(__name__)

    # Step 2: Create a simple GET endpoint
    @app.route('/hello', methods=['GET'])
    def hello():
        """Simple hello endpoint."""
        return jsonify({"message": "Hello, Flask!"})

    # Step 3: Create a personalized greeting
    @app.route('/hello/<name>', methods=['GET'])
    def hello_name(name):
        """Personalized greeting endpoint."""
        return jsonify({"message": f"Hello, {name}!"})

    # Step 4: Create a POST endpoint
    @app.route('/greet', methods=['POST'])
    def greet():
        """Greet endpoint that accepts JSON data."""
        data = request.json

        # Validate that name is provided
        if not data or 'name' not in data:
            return jsonify({"error": "Name is required"}), 400

        name = data['name']
        timestamp = datetime.now().isoformat()

        return jsonify({
            "message": f"Hello, {name}!",
            "timestamp": timestamp
        })

    # Step 5: Return the app
    return app


# Run the application
if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 1 Solution: Hello API")
    print("="*50)
    print("Visit: http://localhost:5000/hello")
    print("Try: http://localhost:5000/hello/YourName")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
