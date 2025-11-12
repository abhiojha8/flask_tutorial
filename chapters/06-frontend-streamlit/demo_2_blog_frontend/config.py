"""
Configuration for Streamlit Frontend
"""

import os

# Backend API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')

# App configuration
APP_TITLE = "Blog Application"
APP_ICON = "📝"

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50

# File upload
MAX_FILE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']
