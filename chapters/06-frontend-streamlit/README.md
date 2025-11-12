# Chapter 6: Frontend Development with Streamlit

## 🎯 Chapter Goals

By the end of this chapter, you will:
- Build interactive web UIs with Streamlit
- Connect frontend to Flask REST API backend
- Implement authentication flow in frontend
- Handle session state and token management
- Make HTTP requests with error handling
- Create forms with real-time validation
- Handle file uploads from frontend to backend
- Build a complete full-stack blog application
- Manage multi-page Streamlit applications

## 📚 What You'll Learn

### Part 1: Streamlit Fundamentals
- Installing and setting up Streamlit
- Basic components (text, headers, markdown)
- Input widgets (text, number, selectbox, slider)
- Buttons and forms
- Layout management (columns, sidebar, containers)
- Session state management
- File uploaders and media display
- Data visualization (tables, charts)

### Part 2: Backend Integration
- Making HTTP requests with `requests` library
- API client design patterns
- Error handling and user feedback
- Loading states and spinners
- JWT token management
- Authentication flow implementation
- CRUD operations from frontend

### Part 3: Full-Stack Application
- Multi-page app architecture
- Protected routes and navigation
- Form validation (frontend + backend)
- File upload with progress
- Real-time data updates
- Responsive layout design
- State persistence across pages

## 🚀 Demo Projects

### Demo 1: Streamlit Basics (`demo_1_streamlit_basics/`)

A comprehensive introduction to Streamlit components and features.

**What you'll see:**
- All major Streamlit widgets
- Layout options (columns, sidebar, expander)
- Session state examples
- Form handling
- File upload demo
- Data display (dataframes, charts)

**Run it:**
```bash
cd demo_1_streamlit_basics
pip install -r requirements.txt
streamlit run app.py
```

### Demo 2: Full-Stack Blog Application (`demo_2_blog_frontend/`)

A complete blog frontend that connects to Flask backend from previous chapters.

**Features:**
- 🔐 User authentication (login, register, logout)
- 📝 Article management (create, read, update, delete)
- 💬 Comment system
- 👤 Author profiles
- 🖼️ Image upload for articles
- 🔍 Search and filtering
- 📄 Pagination
- ✅ Real-time validation

**Architecture:**
```
Frontend (Streamlit)  ←→  Backend (Flask REST API)
     Port 8501              Port 5000

Pages:
- Home (article listing)
- Create Article
- Article Detail
- Authors
- Login/Register
- User Dashboard
```

**Run it:**
```bash
# Terminal 1: Start backend
cd backend
python app.py

# Terminal 2: Start frontend
cd demo_2_blog_frontend
streamlit run app.py
```

## 💻 Exercises

### Exercise 1: Basic Streamlit UI 🟢
**Topics:** Components, layout, widgets
- Build a simple blog homepage with Streamlit
- Display hardcoded articles in cards
- Add search box and category filter
- Implement pagination
- Use columns for responsive layout

### Exercise 2: API Integration 🟢
**Topics:** HTTP requests, error handling, state management
- Connect to Flask backend
- Fetch and display real articles
- Handle loading states with spinners
- Show error messages from API
- Add refresh button

### Exercise 3: Authentication Flow 🟡
**Topics:** JWT tokens, session state, protected pages
- Implement login page
- Store JWT token in session state
- Create protected pages with authentication check
- Add logout functionality
- Handle token expiration gracefully

### Exercise 4: CRUD Operations 🟡
**Topics:** Forms, validation, API calls
- Create article form with validation
- Submit to backend API
- Handle validation errors from backend
- Update existing articles
- Delete with confirmation dialog
- Redirect after success

### Exercise 5: File Upload 🔴
**Topics:** File handling, multipart requests, progress
- Add image upload to article form
- Validate file type and size on frontend
- Send multipart request to backend
- Display uploaded image preview
- Handle upload errors
- Show upload progress

## 📖 Key Concepts

### What is Streamlit?

**Streamlit** is a Python library for building interactive web applications without writing HTML/CSS/JavaScript.

```python
import streamlit as st

# Simple app in 3 lines!
st.title("My First App")
name = st.text_input("What's your name?")
st.write(f"Hello, {name}!")
```

**Why Streamlit for this tutorial?**
- ✅ Pure Python - no JavaScript needed
- ✅ Fast prototyping
- ✅ Built-in widgets and layouts
- ✅ Perfect for data apps and dashboards
- ✅ Easy deployment (Streamlit Cloud)

### Streamlit vs Traditional Frontend

```
Traditional Web App:
═══════════════════
HTML → Structure
CSS → Styling
JavaScript → Interactivity
Framework → React/Vue/Angular

Streamlit App:
═════════════
Python → Everything!
```

### Session State Management

Streamlit reruns your script on every interaction. Use `st.session_state` to persist data:

```python
# Initialize state
if 'count' not in st.session_state:
    st.session_state.count = 0

# Update state
if st.button('Increment'):
    st.session_state.count += 1

# Use state
st.write(f"Count: {st.session_state.count}")
```

### Making API Calls

```python
import requests

# GET request
response = requests.get('http://localhost:5000/api/articles')
if response.status_code == 200:
    articles = response.json()
    st.dataframe(articles)
else:
    st.error(f"Error: {response.status_code}")

# POST request with authentication
headers = {'Authorization': f'Bearer {token}'}
data = {'title': 'My Article', 'content': '...'}

response = requests.post(
    'http://localhost:5000/api/articles',
    json=data,
    headers=headers
)
```

### Authentication Flow

```
1. User Login
   ├─ Enter email/password
   ├─ POST /api/auth/login
   └─ Receive JWT token

2. Store Token
   └─ st.session_state['token'] = token

3. Protected Requests
   └─ headers = {'Authorization': f'Bearer {token}'}

4. Check Auth Status
   ├─ GET /api/auth/me with token
   └─ If 401 → Redirect to login

5. Logout
   ├─ Clear st.session_state['token']
   └─ Redirect to home
```

### Multi-Page Apps

Streamlit automatically creates navigation from files in `pages/` folder:

```
app.py                    → Home (main page)
pages/
  ├─ 1_📝_Articles.py     → Articles page
  ├─ 2_✍️_Create.py        → Create page
  └─ 3_🔐_Login.py         → Login page
```

**Navigation is automatic!** Emojis in filename become icons.

## 🛠️ Technologies Used

- **Streamlit**: Frontend framework
- **requests**: HTTP client for API calls
- **Pillow (PIL)**: Image handling
- **pandas**: Data display (optional)
- **Flask Backend**: From Chapters 1-5

## 📝 Prerequisites

- Completed Chapter 5 (Data Validation)
- Understanding of HTTP requests
- Basic Python knowledge
- Familiarity with REST APIs

## 🚦 Ready Check

Before starting, you should be able to:
- [ ] Create Flask REST API endpoints
- [ ] Understand JWT authentication
- [ ] Make HTTP requests with status codes
- [ ] Handle JSON data
- [ ] Work with Python dictionaries

## 🏗️ Backend API for Chapter 6

We use a **unified backend** combining concepts from all previous chapters:

**Endpoints Available:**

```
Authentication:
POST   /api/auth/register    - Create account
POST   /api/auth/login       - Get JWT token
GET    /api/auth/me          - Get current user

Articles:
GET    /api/articles         - List articles (with filters)
POST   /api/articles         - Create article (auth required)
GET    /api/articles/{id}    - Get article details
PUT    /api/articles/{id}    - Update article (auth required)
DELETE /api/articles/{id}    - Delete article (auth required)
POST   /api/articles/{id}/image - Upload image (auth required)

Comments:
GET    /api/articles/{id}/comments - List comments
POST   /api/articles/{id}/comments - Add comment

Authors:
GET    /api/authors          - List all authors
GET    /api/authors/{id}     - Get author details
GET    /api/authors/{id}/articles - Get author's articles
```

**Query Parameters:**
```
/api/articles?published=true&category=Technology&page=1&per_page=10
```

## 📊 Common Streamlit Patterns

### Pattern 1: Loading States

```python
with st.spinner('Loading articles...'):
    response = requests.get(API_URL)
    if response.ok:
        articles = response.json()
        st.success('Loaded!')
```

### Pattern 2: Error Handling

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    st.success('Article created!')
except requests.exceptions.HTTPError as e:
    st.error(f'Error: {e.response.json()["message"]}')
```

### Pattern 3: Forms with Validation

```python
with st.form('article_form'):
    title = st.text_input('Title', max_chars=200)
    content = st.text_area('Content', height=300)

    submitted = st.form_submit_button('Create Article')

    if submitted:
        if len(title) < 5:
            st.error('Title must be at least 5 characters')
        elif len(content) < 50:
            st.error('Content must be at least 50 characters')
        else:
            # Call API
            create_article(title, content)
```

### Pattern 4: Protected Pages

```python
def require_auth():
    """Check if user is authenticated"""
    if 'token' not in st.session_state:
        st.warning('Please login to access this page')
        st.stop()

    # Verify token is valid
    response = requests.get(
        f'{API_URL}/auth/me',
        headers={'Authorization': f'Bearer {st.session_state.token}'}
    )

    if response.status_code == 401:
        st.error('Session expired. Please login again.')
        del st.session_state['token']
        st.stop()

# Use in protected pages
require_auth()
st.title('Protected Page')
```

### Pattern 5: File Upload

```python
uploaded_file = st.file_uploader(
    'Choose an image',
    type=['jpg', 'jpeg', 'png'],
    accept_multiple_files=False
)

if uploaded_file:
    # Validate size
    if uploaded_file.size > 5 * 1024 * 1024:
        st.error('File too large (max 5MB)')
    else:
        # Preview
        st.image(uploaded_file)

        # Upload to backend
        files = {'file': uploaded_file}
        response = requests.post(
            f'{API_URL}/articles/{article_id}/image',
            files=files,
            headers={'Authorization': f'Bearer {token}'}
        )
```

## 🎨 Streamlit Layout Examples

### Two Columns

```python
col1, col2 = st.columns(2)

with col1:
    st.header('Left Column')
    st.write('Content here')

with col2:
    st.header('Right Column')
    st.write('Content here')
```

### Sidebar

```python
with st.sidebar:
    st.header('Filters')
    category = st.selectbox('Category', categories)
    published = st.checkbox('Published only')

    if st.button('Apply Filters'):
        st.rerun()
```

### Tabs

```python
tab1, tab2, tab3 = st.tabs(['Articles', 'Authors', 'Categories'])

with tab1:
    st.write('Article content')

with tab2:
    st.write('Author content')

with tab3:
    st.write('Category content')
```

## 🚨 Common Mistakes to Avoid

### ❌ Not handling session state properly
```python
# Wrong - will reset on every rerun
count = 0

# Right - persists across reruns
if 'count' not in st.session_state:
    st.session_state.count = 0
```

### ❌ Not checking API response status
```python
# Wrong
response = requests.get(url)
data = response.json()  # Might fail!

# Right
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
else:
    st.error(f'Error: {response.status_code}')
```

### ❌ Hardcoding backend URL
```python
# Wrong
url = 'http://localhost:5000/api/articles'

# Right
from config import API_BASE_URL
url = f'{API_BASE_URL}/articles'
```

### ❌ Not handling loading states
```python
# Wrong - appears frozen during request
articles = requests.get(url).json()

# Right - shows loading spinner
with st.spinner('Loading...'):
    articles = requests.get(url).json()
```

### ❌ Exposing sensitive data
```python
# Wrong - token visible in UI
st.write(f'Token: {st.session_state.token}')

# Right - never display tokens
# Store in session_state but don't show
```

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Python requests Library](https://requests.readthedocs.io/)
- [JWT.io](https://jwt.io/) - Decode and verify JWTs

## 🎯 Learning Outcomes

After completing this chapter, you will be able to:

✅ Build interactive UIs with Streamlit
✅ Connect frontend to Flask REST APIs
✅ Implement JWT authentication flow
✅ Manage session state effectively
✅ Make HTTP requests with proper error handling
✅ Create forms with validation
✅ Handle file uploads
✅ Build multi-page applications
✅ Deploy full-stack applications
✅ Debug frontend-backend integration issues

## ⏭️ Next Steps

After Chapter 6, you'll have a complete full-stack blog application! Next chapters could cover:
- Testing (unittest, pytest)
- Deployment (Docker, AWS, Heroku)
- Performance optimization
- Advanced features (websockets, caching)
- Monitoring and logging

## 🌐 Deployment

### Streamlit Cloud (Frontend)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Deploy!

### Railway/Render (Backend)
1. Push Flask app to GitHub
2. Connect to Railway/Render
3. Set environment variables
4. Deploy!

### Update Frontend Config
```python
# config.py
import os

# Use environment variable for production
API_BASE_URL = os.getenv(
    'API_BASE_URL',
    'http://localhost:5000/api'  # Local development
)
```

---

**Ready to build beautiful frontends?** Start with [Demo 1: Streamlit Basics](demo_1_streamlit_basics/README.md)!

**Then build a full-stack app:** [Demo 2: Blog Frontend](demo_2_blog_frontend/README.md)!
