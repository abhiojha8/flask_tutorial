# Chapter 1: Flask API Development Environment

## 🎯 Chapter Overview

In this chapter, you'll set up a professional Flask API development environment and build your first API with automatic Swagger documentation, similar to FastAPI. We'll focus on backend fundamentals and API-first development.

## 📚 What You'll Learn

- Setting up Flask with application factory pattern
- Integrating Flask-RESTX for automatic Swagger UI
- Structuring Flask projects for scalability
- Configuration management for different environments
- Logging setup for production-ready APIs
- Creating your first documented API endpoints

## 🛠️ Prerequisites

- Python 3.11+ installed
- Basic Python knowledge
- Command line familiarity
- Code editor (VS Code recommended)

## 📂 Chapter Structure

```
01-flask-basics/
├── README.md           # This file
├── tutorial.md         # Detailed tutorial
├── demo/              # Complete working example
│   ├── app.py         # Main application
│   ├── config.py      # Configuration
│   ├── requirements.txt
│   └── README.md
├── exercises/         # Practice exercises
│   └── README.md
├── solutions/         # Exercise solutions
└── tests/            # Test examples
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd chapters/01-flask-basics/demo
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

### 3. Access Swagger UI

Open your browser and navigate to:
```
http://localhost:5000/swagger
```

## 🎮 Demo Application

The demo application showcases:
- Basic Flask setup with Flask-RESTX
- Swagger UI integration
- Environment-based configuration
- Structured logging
- Error handling
- Health check endpoints

## 📝 Key Concepts

### 1. Application Factory Pattern
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    api.init_app(app)

    return app
```

### 2. Flask-RESTX Integration
```python
from flask_restx import Api, Resource, fields

api = Api(
    title='Flask API',
    version='1.0',
    description='Professional Flask API with Swagger UI',
    doc='/swagger'
)
```

### 3. Resource-Based Endpoints
```python
@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        """Returns a greeting message"""
        return {'message': 'Hello, World!'}
```

## 💡 Exercises

### Exercise 1: Environment Configuration (🟢 Basic)
Create a multi-environment configuration system supporting development, testing, and production.

### Exercise 2: Structured Logging (🟢 Basic)
Implement JSON-formatted logging with request IDs for API tracking.

### Exercise 3: Health Check System (🟡 Intermediate)
Build comprehensive health check endpoints reporting system status.

### Exercise 4: Error Handling (🟡 Intermediate)
Create custom error handlers with proper HTTP status codes and messages.

### Exercise 5: API Versioning (🔴 Advanced)
Implement API versioning with backward compatibility.

## 🧪 Testing

Run the tests:
```bash
cd tests
pytest test_app.py -v
```

## 📊 Learning Outcomes

After completing this chapter, you will be able to:
- ✅ Set up a professional Flask development environment
- ✅ Create APIs with automatic Swagger documentation
- ✅ Implement proper project structure
- ✅ Configure applications for different environments
- ✅ Add comprehensive logging to APIs
- ✅ Handle errors professionally

## 🔗 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-RESTX Documentation](https://flask-restx.readthedocs.io/)
- [Swagger/OpenAPI Specification](https://swagger.io/specification/)

## ⏭️ Next Chapter

[Chapter 2: RESTful API Design with Swagger](../02-restful-apis/README.md) - Learn to design and build complete RESTful APIs with full CRUD operations and comprehensive documentation.

---

**Ready to build your first API?** Start with the [tutorial](tutorial.md)!