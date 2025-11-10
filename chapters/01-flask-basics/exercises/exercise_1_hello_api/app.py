"""
Exercise 1: Hello API - Your First Flask Application

Learning Objectives:
- Create a basic Flask application
- Define simple routes with different HTTP methods
- Return JSON responses
- Use factory pattern

TODO: Complete the marked sections to create your first API!
"""

from flask import Flask, jsonify

def create_app():
    """
    Create and configure the Flask application.

    TODO: Follow the steps below to build your first API!
    """
    # Step 1: Create Flask instance
    # TODO: Create the Flask app instance
    # Hint: app = Flask(__name__)


    # Step 2: Create a simple GET endpoint
    # TODO: Create a route for GET /hello that returns a JSON message
    # Hint: Use @app.route('/hello', methods=['GET'])
    # Return: {"message": "Hello, Flask!"}


    # Step 3: Create a personalized greeting
    # TODO: Create a route for GET /hello/<name> that returns a personalized message
    # Hint: Use @app.route('/hello/<name>', methods=['GET'])
    # Return: {"message": "Hello, <name>!"}


    # Step 4: Create a POST endpoint
    # TODO: Create a route for POST /greet that accepts JSON data and returns a greeting
    # Hint: Use request.json to get the JSON body
    # Expected input: {"name": "Alice"}
    # Return: {"message": "Hello, Alice!", "timestamp": <current time>}


    # Step 5: Return the app
    # TODO: Return the configured app
    # Hint: return app



# Run the application
if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("Exercise 1: Hello API")
    print("="*50)
    print("Visit: http://localhost:5000/hello")
    print("Try: http://localhost:5000/hello/YourName")
    print("="*50 + "\n")

    app.run(debug=True, port=5000)
