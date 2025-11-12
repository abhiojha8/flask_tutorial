# Demo 2: Full-Stack Blog Frontend

A complete blog application frontend built with Streamlit that connects to the Flask backend API.

## What's Included

This demo demonstrates a **real-world full-stack application** integrating all concepts from Chapters 1-6:

### 🔐 Authentication
- User registration and login
- JWT token management
- Session state persistence
- Protected routes

### 📝 Article Management
- Browse all articles with pagination
- View detailed article content
- Create new articles
- Edit existing articles (owner only)
- Delete articles (owner only)
- Upload article images
- Draft/publish status

### 💬 Comments System
- View all comments on articles
- Post comments (authenticated users)
- Delete comments (owner or article author)
- Real-time comment count

### 👤 Author Profiles
- View all authors
- Individual author profiles
- Author statistics
- List of author's articles

### 🎨 Advanced Features
- Search and filter articles
- Category selection
- Tag management
- View counters
- Metrics dashboard
- Error handling
- Backend status check

## Architecture

```
demo_2_blog_frontend/
├── app.py                      # Main home page
├── config.py                   # Configuration settings
├── requirements.txt            # Dependencies
├── utils/
│   ├── auth.py                # Authentication helpers
│   └── api_client.py          # API client wrapper
└── pages/
    ├── 1_📝_Articles.py       # Article detail view
    ├── 2_✍️_Create_Article.py # Create/edit articles
    ├── 3_👤_Authors.py         # Author listing/profiles
    └── 4_🔐_Login.py           # Login/registration
```

## Prerequisites

### 1. Backend Must Be Running

Before starting the frontend, ensure the backend is running:

```bash
# Navigate to backend directory
cd ../backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the backend
python app.py
```

Backend should be running at `http://localhost:5000`

### 2. Database Setup

The backend automatically creates sample data on first run:
- 3 demo users
- 5 sample articles
- Multiple comments

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 3. Login with Demo Account

Use any of these demo credentials:

**User 1:**
- Email: `john.doe@example.com`
- Password: `password123`

**User 2:**
- Email: `jane.smith@example.com`
- Password: `password123`

**User 3:**
- Email: `bob.johnson@example.com`
- Password: `password123`

## Features Walkthrough

### 1. Home Page (app.py)

**Features:**
- Browse recent articles
- Search and filter
- Pagination
- Quick stats dashboard
- Backend connection status

**Key Concepts:**
```python
# Session state for pagination
if 'home_page' not in st.session_state:
    st.session_state.home_page = 1

# API call with parameters
params = {
    'page': st.session_state.home_page,
    'per_page': DEFAULT_PAGE_SIZE,
    **st.session_state.home_filters
}
response = api.get_articles(params=params)
```

### 2. Articles Page

**Features:**
- View full article content
- See article metadata and stats
- Read all comments
- Post comments (authenticated)
- Delete comments (owner)
- Edit article (owner)

**Key Concepts:**
```python
# Protected actions
if is_authenticated() and st.session_state.user['id'] == article['author']['id']:
    if st.button("✏️ Edit Article"):
        st.session_state.edit_article_id = article_id
        st.switch_page("pages/2_✍️_Create_Article.py")
```

### 3. Create/Edit Article Page

**Features:**
- Create new articles
- Edit existing articles
- Upload images
- Markdown support
- Draft/publish toggle
- Form validation
- Delete article

**Key Concepts:**
```python
# Form validation
errors = []
if not title or not title.strip():
    errors.append("❌ Title is required")
if len(content) < 50:
    errors.append("❌ Content must be at least 50 characters")

# API call with authentication
api = BlogAPIClient(API_BASE_URL, st.session_state.token)
new_article = api.create_article(article_data)
```

### 4. Authors Page

**Features:**
- Browse all authors
- View individual profiles
- Author statistics
- Filter by published/draft
- Sort by various criteria

**Key Concepts:**
```python
# Grid layout
cols_per_row = 3
rows = [authors[i:i + cols_per_row] for i in range(0, len(authors), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for idx, author in enumerate(row):
        with cols[idx]:
            # Display author card
```

### 5. Login/Registration Page

**Features:**
- User login
- New user registration
- Form validation
- Email validation
- Password confirmation
- Demo credentials display

**Key Concepts:**
```python
# Login flow
response = api.login(email, password)
save_auth_data(response['access_token'], response['user'])
st.rerun()  # Refresh to show logged-in state
```

## Code Organization

### Configuration (config.py)

Centralized configuration:
```python
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
APP_TITLE = "Blog Application"
DEFAULT_PAGE_SIZE = 10
MAX_FILE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']
```

### Authentication Helpers (utils/auth.py)

Manages authentication state:
```python
def init_session_state()        # Initialize session variables
def is_authenticated()          # Check if user is logged in
def require_auth()              # Redirect if not authenticated
def save_auth_data(token, user) # Save login data
def logout()                    # Clear session and logout
def show_user_info()            # Display user info in sidebar
```

### API Client (utils/api_client.py)

Wrapper for all API calls:
```python
class BlogAPIClient:
    # Authentication
    def login(email, password)
    def register(name, email, password)
    def logout()

    # Articles
    def get_articles(params)
    def get_article(article_id)
    def create_article(data)
    def update_article(article_id, data)
    def delete_article(article_id)
    def upload_article_image(article_id, file)

    # Comments
    def get_comments(article_id)
    def create_comment(article_id, data)
    def delete_comment(article_id, comment_id)

    # Authors
    def get_authors()
    def get_author(author_id)
```

### Error Handling

User-friendly error messages:
```python
def handle_api_error(error: Exception):
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("❌ Cannot connect to backend")
    elif isinstance(error, requests.exceptions.Timeout):
        st.error("⏱️ Request timed out")
    elif isinstance(error, requests.exceptions.HTTPError):
        # Handle by status code
```

## Common Patterns

### Pattern 1: Protected Page

```python
from utils.auth import require_auth

# At the top of the page
require_auth()  # Redirects to login if not authenticated

# Rest of the page code
```

### Pattern 2: API Call with Error Handling

```python
try:
    api = BlogAPIClient(API_BASE_URL, st.session_state.token)
    response = api.get_articles(params)
    articles = response['articles']

    # Display articles
    for article in articles:
        st.write(article['title'])

except Exception as e:
    handle_api_error(e)
```

### Pattern 3: Navigation

```python
# Navigate to another page
if st.button("Go to Articles"):
    st.switch_page("pages/1_📝_Articles.py")

# Pass data between pages
st.session_state.selected_author_id = author_id
st.switch_page("pages/3_👤_Authors.py")
```

### Pattern 4: Form with Validation

```python
with st.form("my_form"):
    title = st.text_input("Title")
    content = st.text_area("Content")
    submit = st.form_submit_button("Submit")

    if submit:
        errors = []
        if not title:
            errors.append("Title required")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # Process form
```

### Pattern 5: Conditional Display

```python
# Show different UI based on authentication
if is_authenticated():
    st.write(f"Welcome, {st.session_state.user['name']}")
    if st.button("Create Article"):
        st.switch_page("pages/2_✍️_Create_Article.py")
else:
    st.info("Please login to create articles")
    if st.button("Go to Login"):
        st.switch_page("pages/4_🔐_Login.py")
```

## Key Concepts Demonstrated

### 1. Full-Stack Architecture

```
Streamlit Frontend → HTTP Requests → Flask Backend → PostgreSQL Database
                   ← JSON Response ←              ←
```

### 2. JWT Authentication

- Token stored in `st.session_state`
- Sent in Authorization header
- Protected routes require valid token
- Logout blacklists token

### 3. Session State Management

```python
# Initialize
if 'token' not in st.session_state:
    st.session_state.token = None

# Update
st.session_state.token = new_token

# Access
if st.session_state.token:
    # User is authenticated
```

### 4. Multi-Page Navigation

```
app.py (Home)
  ├── pages/1_📝_Articles.py
  ├── pages/2_✍️_Create_Article.py
  ├── pages/3_👤_Authors.py
  └── pages/4_🔐_Login.py
```

Streamlit automatically creates sidebar navigation from `pages/` folder.

### 5. Error Handling Strategy

```python
try:
    # API call
    response = api.get_data()
except requests.exceptions.ConnectionError:
    st.error("Backend not available")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        st.error("Please login")
    elif e.response.status_code == 403:
        st.error("Permission denied")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

## Troubleshooting

### "Cannot connect to backend"

**Solution:**
1. Check backend is running: `http://localhost:5000`
2. Check API_BASE_URL in config.py
3. Verify CORS is enabled in backend

### "401 Unauthorized"

**Solution:**
1. Token may have expired - logout and login again
2. Check token is being sent in requests
3. Verify JWT_SECRET_KEY matches in backend

### "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### "Page not loading"

**Solution:**
1. Check Streamlit is running: `streamlit run app.py`
2. Verify port 8501 is available
3. Try clearing cache: `streamlit cache clear`

### "Form not submitting"

**Solution:**
1. Use `st.form()` context manager
2. Use `st.form_submit_button()` not `st.button()`
3. Check validation logic

### "Session state not persisting"

**Solution:**
1. Initialize session state at page start
2. Use `st.session_state['key']` not local variables
3. Check for `st.rerun()` calls

### "Image upload fails"

**Solution:**
1. Check file size < MAX_FILE_SIZE_MB
2. Verify file type in ALLOWED_IMAGE_TYPES
3. Ensure article exists before uploading image
4. Check backend uploads/ directory permissions

## Testing Checklist

- [ ] Backend runs without errors
- [ ] Frontend connects to backend successfully
- [ ] User can register new account
- [ ] User can login with credentials
- [ ] User can view articles
- [ ] User can create article
- [ ] User can edit own article
- [ ] User can delete own article
- [ ] User can upload article image
- [ ] User can view comments
- [ ] User can post comment
- [ ] User can delete own comment
- [ ] Pagination works correctly
- [ ] Search and filters work
- [ ] Author profiles display correctly
- [ ] Logout clears session
- [ ] Error messages are user-friendly
- [ ] Protected routes require authentication

## Learning Objectives

After completing this demo, students will understand:

1. **Full-Stack Integration**
   - How frontend connects to backend
   - HTTP request/response flow
   - API design patterns

2. **Authentication Flow**
   - Registration and login process
   - JWT token management
   - Protected routes

3. **State Management**
   - Session state in Streamlit
   - Persistent vs temporary data
   - Navigation with state

4. **CRUD Operations**
   - Create, Read, Update, Delete
   - Form validation
   - Error handling

5. **Multi-Page Apps**
   - Page organization
   - Navigation between pages
   - Sharing data across pages

6. **Real-World Patterns**
   - API client abstraction
   - Centralized configuration
   - Reusable helper functions
   - User-friendly error messages

## Next Steps

1. **Explore the Code**
   - Read through each file
   - Understand the structure
   - See how components interact

2. **Experiment**
   - Create articles
   - Add comments
   - Upload images
   - Try different filters

3. **Customize**
   - Add new features
   - Modify the UI
   - Enhance validation
   - Improve error handling

4. **Complete Exercises**
   - Practice building similar features
   - Apply the patterns learned
   - Build your own full-stack app

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [Multi-Page Apps](https://docs.streamlit.io/library/get-started/multipage-apps)
- [Session State](https://docs.streamlit.io/library/api-reference/session-state)
- [Requests Library](https://requests.readthedocs.io/)

---

**Full-Stack Blog Application** | Built with Streamlit + Flask

This demo brings together everything learned in Chapters 1-6 into a complete, production-ready application!
