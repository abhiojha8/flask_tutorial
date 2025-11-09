# Chapter 1 Demo: Flask API with Swagger UI

## 🎯 Overview

This demo application showcases a professional Flask API setup with automatic Swagger documentation. It's a simple Task Management API that demonstrates best practices for Flask backend development.

## ✨ Features

- **Swagger UI**: Interactive API documentation at `/swagger`
- **RESTful Design**: Proper HTTP methods and status codes
- **Namespace Organization**: Logical grouping of endpoints
- **Error Handling**: Comprehensive error responses
- **Logging**: Structured logging for debugging
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Checks**: Production-ready health endpoints

## 🚀 Running the Application

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

### 3. Access the API

- **Swagger UI**: http://localhost:5000/swagger
- **API Base URL**: http://localhost:5000/api/v1

## 📍 API Endpoints

### Health Checks
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/ready` - Readiness check

### Task Management
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{task_id}` - Get specific task
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task
- `GET /api/v1/tasks/search` - Search tasks
- `GET /api/v1/tasks/stats` - Get task statistics

## 🧪 Testing with Swagger UI

1. Open http://localhost:5000/swagger in your browser
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in required parameters
5. Click "Execute"
6. View the response

## 📝 Testing with cURL

### Create a Task
```bash
curl -X POST "http://localhost:5000/api/v1/tasks/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Task",
       "description": "This is a test task",
       "completed": false
     }'
```

### List All Tasks
```bash
curl -X GET "http://localhost:5000/api/v1/tasks/" \
     -H "accept: application/json"
```

### Get Task Statistics
```bash
curl -X GET "http://localhost:5000/api/v1/tasks/stats" \
     -H "accept: application/json"
```

### Search Tasks
```bash
curl -X GET "http://localhost:5000/api/v1/tasks/search?q=flask" \
     -H "accept: application/json"
```

## 🔧 Configuration

The application supports three environments:
- **development**: Debug mode enabled, sample data loaded
- **testing**: Testing configuration
- **production**: Production settings

Change the environment in `app.py`:
```python
app = create_app('development')  # or 'testing', 'production'
```

## 📚 Code Structure

```python
# Application factory pattern
def create_app(config_name='development'):
    app = Flask(__name__)
    # Configuration and setup
    return app

# Resource-based endpoints
@tasks_ns.route('/')
class TaskList(Resource):
    @tasks_ns.doc('list_tasks')
    @tasks_ns.marshal_list_with(task_model)
    def get(self):
        """List all tasks"""
        return tasks
```

## 🎓 Learning Points

1. **Flask-RESTX Integration**: Automatic Swagger documentation
2. **Namespace Organization**: Logical API structure
3. **Model Definitions**: Input validation and documentation
4. **Error Handling**: Professional error responses
5. **Logging**: Structured application logging
6. **Factory Pattern**: Flexible application configuration

## 🚦 Next Steps

- Add database integration (Chapter 3)
- Implement authentication (Chapter 4)
- Add data validation (Chapter 5)
- Create unit tests
- Add pagination support

## 📖 References

- [Flask-RESTX Documentation](https://flask-restx.readthedocs.io/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [REST API Best Practices](https://restfulapi.net/)