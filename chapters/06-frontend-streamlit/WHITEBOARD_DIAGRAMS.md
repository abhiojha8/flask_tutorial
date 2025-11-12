# Whiteboard Diagrams for Chapter 6: Frontend with Streamlit

Visual explanations for teaching Streamlit and full-stack integration during live coding sessions.

---

## DIAGRAM 1: Full-Stack Architecture Overview

```
FULL-STACK BLOG APPLICATION
════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                       │
│                      http://localhost:8501                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────▼───────────┐
                │   STREAMLIT FRONTEND  │
                │     (Python App)      │
                ├───────────────────────┤
                │ Pages:                │
                │  ├─ Home              │
                │  ├─ Articles          │
                │  ├─ Create Article    │
                │  ├─ Authors           │
                │  └─ Login/Register    │
                ├───────────────────────┤
                │ State Management:     │
                │  ├─ JWT Token         │
                │  ├─ Current User      │
                │  └─ Form Data         │
                └───────────┬───────────┘
                            │
                            │ HTTP Requests
                            │ (requests library)
                            │
                ┌───────────▼───────────┐
                │   FLASK BACKEND API   │
                │   http://localhost    │
                │        :5000/api      │
                ├───────────────────────┤
                │ Endpoints:            │
                │  POST /auth/login     │
                │  GET  /articles       │
                │  POST /articles       │
                │  GET  /authors        │
                │  POST /comments       │
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │   POSTGRESQL DB       │
                │   (Supabase)          │
                ├───────────────────────┤
                │ Tables:               │
                │  ├─ users             │
                │  ├─ articles          │
                │  ├─ comments          │
                │  └─ authors           │
                └───────────────────────┘

DATA FLOW EXAMPLE:
══════════════════
1. User clicks "Create Article" button (Streamlit)
   ↓
2. Form submission triggers Python function
   ↓
3. requests.post() sends data to Flask API
   ↓
4. Flask validates with Marshmallow
   ↓
5. Flask saves to PostgreSQL
   ↓
6. Flask returns JSON response
   ↓
7. Streamlit displays success message
   ↓
8. Page refreshes with new article
```

---

## DIAGRAM 2: Streamlit Rerun Mechanism

```
HOW STREAMLIT WORKS
═══════════════════

TRADITIONAL WEB APP:                STREAMLIT APP:
════════════════════                ══════════════

Server renders HTML once            Script reruns on EVERY interaction!

User clicks button                  User clicks button
    ↓                                  ↓
JavaScript handles event            ENTIRE Python script reruns
    ↓                                  ↓
DOM updates                         New UI generated
                                       ↓
                                    Browser updates

EXAMPLE:
────────

# app.py
import streamlit as st

st.title("Counter App")              RUN 1: Page loads
                                      ├─ title displays
if 'count' not in st.session_state:   ├─ count = 0
    st.session_state.count = 0        └─ button shows "0"

if st.button(f'Count: {st.session_state.count}'):
    st.session_state.count += 1      RUN 2: Button clicked
                                      ├─ ENTIRE script reruns
st.write(f"Value: {st.session_state.count}")  ├─ count = 1
                                      ├─ button shows "1"
                                      └─ write shows "1"

                                     RUN 3: Button clicked again
                                      ├─ script reruns AGAIN
                                      ├─ count = 2
                                      └─ ...

WHY SESSION STATE?
══════════════════
Without session_state:               With session_state:
───────────────────                  ──────────────────
count = 0                            if 'count' not in st.session_state:
↓                                        st.session_state.count = 0
Resets to 0 every rerun!             ↓
                                     Persists across reruns!
```

---

## DIAGRAM 3: Authentication Flow

```
LOGIN FLOW WITH JWT
═══════════════════

FRONTEND (Streamlit)                 BACKEND (Flask)
════════════════════                ═══════════════

┌──────────────────┐
│  Login Page      │
│  ┌────────────┐  │
│  │ Email:     │  │
│  │ [input]    │  │
│  │ Password:  │  │
│  │ [****]     │  │
│  │ [Login]    │  │
│  └────────────┘  │
└────────┬─────────┘
         │
         │ User clicks Login
         ↓
┌──────────────────┐
│ Validate Input   │
│ ✓ Email not empty│
│ ✓ Password > 8   │
└────────┬─────────┘
         │
         │ POST /api/auth/login
         │ {
         │   "email": "user@example.com",
         │   "password": "secret123"
         │ }
         ↓                              ┌────────────────────┐
    ┌────────────────────────────────>  │ Receive Request    │
    │                                   └─────────┬──────────┘
    │                                             │
    │                                   ┌─────────▼──────────┐
    │                                   │ Validate Schema    │
    │                                   │ (Marshmallow)      │
    │                                   └─────────┬──────────┘
    │                                             │
    │                                   ┌─────────▼──────────┐
    │                                   │ Find user in DB    │
    │                                   │ Check password     │
    │                                   │ (bcrypt)           │
    │                                   └─────────┬──────────┘
    │                                             │
    │                                   ┌─────────▼──────────┐
    │                                   │ Generate JWT       │
    │                                   │ Token (1 hr exp)   │
    │                                   └─────────┬──────────┘
    │                                             │
    │ 200 OK                                      │
    │ {                                           │
    │   "token": "eyJhbGc...",  <─────────────────┘
    │   "user": {
    │     "id": 1,
    │     "username": "john"
    │   }
    │ }
    │
┌───▼───────────────┐
│ Store in Session  │
│ st.session_state  │
│   ['token'] = ... │
│   ['user'] = ...  │
└───────┬───────────┘
        │
┌───────▼───────────┐
│ Redirect to Home  │
│ st.rerun()        │
└───────────────────┘


PROTECTED PAGE ACCESS:
══════════════════════

User visits /create-article
         ↓
┌──────────────────┐
│ Check auth       │
│ if 'token' not   │
│   in session:    │
│   redirect login │
└────────┬─────────┘
         │
         ↓ Token exists
┌──────────────────┐
│ Verify token     │
│ GET /auth/me     │
│ Authorization:   │
│ Bearer <token>   │
└────────┬─────────┘
         │                             ┌────────────────────┐
         │──────────────────────────>  │ Decode JWT         │
         │                             │ Check expiration   │
         │                             │ Check signature    │
         │                             └─────────┬──────────┘
         │                                       │
         │  200 OK                               │
         │  {"id": 1, "username": "john"} <──────┘
         │
┌────────▼─────────┐
│ Show Protected   │
│ Page Content     │
└──────────────────┘
```

---

## DIAGRAM 4: API Request Flow

```
CREATING AN ARTICLE
═══════════════════

STREAMLIT FRONTEND                   FLASK BACKEND
══════════════════                  ═════════════

┌──────────────────────┐
│ Article Form         │
│ ┌──────────────────┐ │
│ │Title: [input]    │ │
│ │Content: [text]   │ │
│ │Category: [select]│ │
│ │Tags: [chips]     │ │
│ │[Submit]          │ │
│ └──────────────────┘ │
└──────────┬───────────┘
           │
           │ User clicks Submit
           ↓
┌──────────────────────┐
│ Frontend Validation  │
│ ✓ Title >= 5 chars   │
│ ✓ Content >= 50 chars│
│ ✓ Category selected  │
└──────────┬───────────┘
           │
           │ Show spinner
           ↓
┌──────────────────────┐
│ with st.spinner():   │
│   Make API call      │
└──────────┬───────────┘
           │
           │ POST /api/articles
           │ Headers:
           │   Authorization: Bearer <token>
           │ Body:
           │ {
           │   "title": "My Article",
           │   "content": "...",
           │   "category": "Tech",
           │   "tags": ["python", "flask"]
           │ }
           ↓                              ┌──────────────────┐
      ┌────────────────────────────────>  │ Receive Request  │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Verify JWT Token │
      │                                   │ @jwt_required    │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Validate Data    │
      │                                   │ Marshmallow      │
      │                                   │ ArticleSchema    │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Business Logic   │
      │                                   │ - Create slug    │
      │                                   │ - Set author_id  │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Save to Database │
      │                                   │ db.session.add() │
      │                                   │ db.session.      │
      │                                   │   commit()       │
      │                                   └────────┬─────────┘
      │                                            │
      │  201 Created                               │
      │  {                                         │
      │    "id": 123,          <───────────────────┘
      │    "title": "My Article",
      │    "slug": "my-article",
      │    "created_at": "..."
      │  }
      │
┌─────▼──────────────────┐
│ Handle Response        │
│ if response.ok:        │
│   st.success(...)      │
│   st.rerun()           │
│ else:                  │
│   st.error(...)        │
└────────────────────────┘


ERROR HANDLING:
═══════════════

try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx

    st.success('Article created!')
    st.balloons()

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        # Validation error
        errors = e.response.json().get('errors', {})
        for field, messages in errors.items():
            st.error(f'{field}: {", ".join(messages)}')

    elif e.response.status_code == 401:
        # Unauthorized
        st.error('Session expired. Please login again.')
        del st.session_state['token']

    else:
        st.error(f'Error: {e.response.status_code}')

except requests.exceptions.ConnectionError:
    st.error('Cannot connect to backend. Is it running?')
```

---

## DIAGRAM 5: Session State Management

```
SESSION STATE ACROSS PAGES
══════════════════════════

MULTI-PAGE STREAMLIT APP:

app.py (Home)                st.session_state (SHARED!)
pages/
  ├─ 1_Articles.py           ┌──────────────────────┐
  ├─ 2_Create.py             │ {                    │
  └─ 3_Login.py              │   'token': 'eyJ...'  │
                             │   'user': {          │
                             │     'id': 1,         │
User navigates between       │     'username': 'j'  │
pages → state persists!      │   },                 │
                             │   'articles_page': 2 │
                             │   'selected_cat': 'T'│
                             │ }                    │
                             └──────────────────────┘

FLOW EXAMPLE:
═════════════

┌────────────────────────┐
│ Page: Login            │
│                        │
│ User enters:           │
│   email, password      │
│   ↓                    │
│ POST /api/auth/login   │
│   ↓                    │
│ Receive token          │
│   ↓                    │
│ st.session_state       │ ────┐
│   ['token'] = token    │     │
│   ['user'] = user      │     │
└────────────────────────┘     │
                               │ STATE SHARED!
┌────────────────────────┐     │
│ User clicks "Articles" │     │
│ (navigates to page 1)  │     │
│                        │     │
│ Page: Articles         │ ◄───┘
│                        │
│ def require_auth():    │
│   if 'token' not in    │
│     st.session_state:  │ ◄─── Token found!
│       redirect login   │
│                        │
│ GET /articles          │
│ Authorization: Bearer  │
│   {st.session_state    │
│     ['token']}         │ ◄─── Uses stored token
└────────────────────────┘


INITIALIZATION PATTERN:
═══════════════════════

# app.py or each page
def init_session_state():
    """Initialize session state variables"""
    if 'token' not in st.session_state:
        st.session_state.token = None

    if 'user' not in st.session_state:
        st.session_state.user = None

    if 'articles_page' not in st.session_state:
        st.session_state.articles_page = 1

# Call at start of each page
init_session_state()


CLEARING STATE (LOGOUT):
════════════════════════

def logout():
    """Clear authentication state"""
    if 'token' in st.session_state:
        del st.session_state['token']

    if 'user' in st.session_state:
        del st.session_state['user']

    st.success('Logged out successfully')
    st.rerun()
```

---

## DIAGRAM 6: File Upload Flow

```
IMAGE UPLOAD FOR ARTICLE
════════════════════════

FRONTEND                             BACKEND
════════                            ════════

┌──────────────────────┐
│ Upload Widget        │
│ st.file_uploader()   │
│                      │
│ [Choose File...]     │
└──────────┬───────────┘
           │
           │ User selects image.jpg
           ↓
┌──────────────────────┐
│ uploaded_file object │
│  .name = "image.jpg" │
│  .size = 524288      │
│  .type = "image/jpeg"│
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ Frontend Validation  │
│ ✓ Type in [jpg,png]  │
│ ✓ Size < 5MB         │
└──────────┬───────────┘
           │
           ↓ Valid
┌──────────────────────┐
│ Preview Image        │
│ st.image(file)       │
└──────────┬───────────┘
           │
           │ User clicks Upload
           ↓
┌──────────────────────┐
│ Prepare Request      │
│ files = {            │
│   'file': uploaded_  │
│           file       │
│ }                    │
│ headers = {          │
│   'Authorization':   │
│   'Bearer <token>'   │
│ }                    │
└──────────┬───────────┘
           │
           │ POST /api/articles/123/image
           │ Content-Type: multipart/form-data
           │ [Binary file data]
           ↓                              ┌──────────────────┐
      ┌────────────────────────────────>  │ Receive File     │
      │                                   │ request.files    │
      │                                   │   ['file']       │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Validate File    │
      │                                   │ - Size check     │
      │                                   │ - Extension      │
      │                                   │ - MIME type      │
      │                                   │ - Dimensions     │
      │                                   │   (PIL)          │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Secure Filename  │
      │                                   │ werkzeug         │
      │                                   │ .secure_filename │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Save File        │
      │                                   │ /uploads/        │
      │                                   │   article_123_   │
      │                                   │   timestamp.jpg  │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Update DB        │
      │                                   │ article.image_   │
      │                                   │   url = "/..."   │
      │                                   └────────┬─────────┘
      │                                            │
      │  200 OK                                    │
      │  {                                         │
      │    "image_url": "/uploads/..." <───────────┘
      │  }
      │
┌─────▼──────────────────┐
│ Show Success           │
│ st.success(...)        │
│ Display uploaded image │
└────────────────────────┘


VALIDATION LAYERS:
══════════════════

Layer 1 (Frontend):              Layer 2 (Backend):
───────────────────              ──────────────────
✓ File type                      ✓ MIME verification
✓ File size                      ✓ Actual image check
✓ User feedback                  ✓ Dimensions
                                 ✓ Malware prevention
```

---

## DIAGRAM 7: Streamlit Components Overview

```
STREAMLIT WIDGET CATEGORIES
════════════════════════════

TEXT & DISPLAY:
═══════════════
st.title("Title")                 # Large heading
st.header("Header")                # Medium heading
st.subheader("Subheader")          # Small heading
st.text("Fixed width text")        # Code-like
st.markdown("**Bold** text")       # Formatted
st.write("Anything!")              # Smart display

INPUT WIDGETS:
══════════════
st.text_input("Name")              # Single line
st.text_area("Bio")                # Multiple lines
st.number_input("Age", 0, 100)     # Number
st.slider("Rating", 1, 5)          # Slider
st.selectbox("Category", [...])    # Dropdown
st.multiselect("Tags", [...])      # Multiple choice
st.checkbox("Published")           # Boolean
st.radio("Status", [...])          # Radio buttons
st.date_input("Date")              # Date picker
st.time_input("Time")              # Time picker
st.file_uploader("Image")          # File selector

BUTTONS & ACTIONS:
══════════════════
st.button("Click me")              # Regular button
st.download_button("DL", data)     # Download
st.form_submit_button("Submit")    # Form submit

DATA DISPLAY:
═════════════
st.dataframe(df)                   # Interactive table
st.table(df)                       # Static table
st.json(data)                      # JSON viewer
st.metric("Visitors", 1234, "+5%") # Metric card

MEDIA:
══════
st.image(img)                      # Image
st.audio(audio)                    # Audio player
st.video(video)                    # Video player

LAYOUT:
═══════
st.columns([1, 2])                 # Columns
st.tabs(["Tab1", "Tab2"])          # Tabs
st.expander("Details")             # Collapsible
st.container()                     # Container
st.sidebar                         # Sidebar
st.empty()                         # Placeholder

FEEDBACK:
═════════
st.success("Success!")             # Green box
st.info("Info")                    # Blue box
st.warning("Warning")              # Yellow box
st.error("Error")                  # Red box
st.spinner("Loading...")           # Loading spinner
st.progress(0.5)                   # Progress bar
st.balloons()                      # Celebration!

CONTROL FLOW:
═════════════
st.stop()                          # Stop execution
st.rerun()                         # Rerun script
st.experimental_rerun()            # Force rerun
```

---

## DIAGRAM 8: Article Listing with Pagination

```
ARTICLE LIST PAGE
═════════════════

┌──────────────────────────────────────────────────┐
│  Filters Sidebar          │  Main Content        │
├───────────────────────────┼──────────────────────┤
│ 🔍 Search:                │  Articles (Page 2/5) │
│ [search box]              │                      │
│                           │  ┌────────────────┐  │
│ 📁 Category:              │  │ Article #11    │  │
│ [ All ▼ ]                 │  │ By: John       │  │
│                           │  │ Tech | 5 💬    │  │
│ 📌 Status:                │  │ [Read] [Edit]  │  │
│ [✓] Published only        │  └────────────────┘  │
│                           │                      │
│ [Apply Filters]           │  ┌────────────────┐  │
│                           │  │ Article #12    │  │
│                           │  │ By: Jane       │  │
│ Results: 45 articles      │  │ Science | 3 💬 │  │
│                           │  │ [Read]         │  │
│                           │  └────────────────┘  │
│                           │                      │
│                           │  ... (8 more)        │
│                           │                      │
│                           │  [< Prev] [Next >]   │
│                           │  Page 2 of 5         │
└───────────────────────────┴──────────────────────┘

CODE STRUCTURE:
═══════════════

# Sidebar filters
with st.sidebar:
    search = st.text_input("Search")
    category = st.selectbox("Category", ["All", "Tech", ...])
    published_only = st.checkbox("Published only")

    if st.button("Apply Filters"):
        st.session_state.filters = {
            'search': search,
            'category': category if category != "All" else None,
            'published': published_only
        }

# Pagination state
if 'page' not in st.session_state:
    st.session_state.page = 1

# Fetch articles
params = {
    'page': st.session_state.page,
    'per_page': 10,
    **st.session_state.get('filters', {})
}

response = requests.get(f'{API_URL}/articles', params=params)
data = response.json()

articles = data['articles']
pagination = data['pagination']

# Display articles
for article in articles:
    with st.container():
        st.subheader(article['title'])
        st.write(f"By: {article['author']['name']}")
        st.write(f"{article['category']} | {article['comment_count']} 💬")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Read", key=f"read_{article['id']}"):
                st.session_state.selected_article = article['id']

        with col2:
            if is_owner(article):
                if st.button("Edit", key=f"edit_{article['id']}"):
                    st.session_state.edit_article = article['id']

# Pagination controls
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.session_state.page > 1:
        if st.button("← Previous"):
            st.session_state.page -= 1
            st.rerun()

with col2:
    st.write(f"Page {pagination['page']} of {pagination['pages']}")

with col3:
    if st.session_state.page < pagination['pages']:
        if st.button("Next →"):
            st.session_state.page += 1
            st.rerun()
```

---

## DIAGRAM 9: Form Validation Pattern

```
ARTICLE CREATION FORM
═════════════════════

CLIENT-SIDE VALIDATION          SERVER-SIDE VALIDATION
══════════════════════          ══════════════════════

┌──────────────────────┐
│ Create Article Form  │
│ ┌──────────────────┐ │
│ │ Title:           │ │
│ │ [My Article___]  │ │  ──┐
│ │                  │ │    │ Frontend checks:
│ │ Content:         │ │    │ - Not empty
│ │ [Text area...]   │ │    │ - Min length
│ │                  │ │    │ - Max length
│ │ Category:        │ │  ──┘
│ │ [Technology ▼]   │ │
│ │                  │ │
│ │ [Submit]         │ │
│ └──────────────────┘ │
└──────────┬───────────┘
           │
           │ Validate before submit
           ↓
┌──────────────────────┐
│ Frontend Validation  │
│                      │
│ if len(title) < 5:   │
│   st.error("Too      │
│     short!")         │
│   st.stop()          │
│                      │
│ if len(content)<50:  │
│   st.error(...)      │
│   st.stop()          │
└──────────┬───────────┘
           │
           │ All checks pass
           ↓
┌──────────────────────┐
│ Show Loading         │
│ with st.spinner():   │
└──────────┬───────────┘
           │
           │ POST /api/articles
           ↓                              ┌──────────────────┐
      ┌────────────────────────────────>  │ Backend Receives │
      │                                   └────────┬─────────┘
      │                                            │
      │                                   ┌────────▼─────────┐
      │                                   │ Marshmallow      │
      │                                   │ Validation:      │
      │                                   │ - Type checking  │
      │                                   │ - Length rules   │
      │                                   │ - Custom         │
      │                                   │   validators     │
      │                                   │ - Business logic │
      │                                   └────────┬─────────┘
      │                                            │
      │  ✅ Success (201)                          │ ✅ Valid
      │  {                                         │
      │    "id": 123,          <───────────────────┘
      │    "title": "...",
      │    ...
      │  }
      │
┌─────▼──────────────────┐
│ Success!               │
│ st.success(...)        │
│ st.balloons()          │
│ st.rerun()             │
└────────────────────────┘

      │  ❌ Validation Error (400)
      │  {
      │    "errors": {
      │      "title": ["Too short"],
      │      "content": ["Required"]
      │    }
      │  }
      │
┌─────▼──────────────────┐
│ Show Errors            │
│ for field, msgs in     │
│   errors.items():      │
│   st.error(            │
│     f"{field}:         │
│       {msgs}"          │
│   )                    │
└────────────────────────┘


WHY VALIDATE TWICE?
═══════════════════

Frontend:                        Backend:
─────────                       ─────────
✓ Immediate feedback            ✓ Security (can't bypass)
✓ Better UX                     ✓ Data integrity
✓ Reduce server load            ✓ Consistent validation
✓ Guide user input              ✓ Business rules

🛡️ NEVER trust frontend validation alone!
```

---

## DIAGRAM 10: Error Handling Strategy

```
COMPREHENSIVE ERROR HANDLING
════════════════════════════

REQUEST LIFECYCLE:
══════════════════

try:
    ┌────────────────────────────────────┐
    │ Make API Request                   │
    │ response = requests.post(...)      │
    └────────────┬───────────────────────┘
                 │
    ┌────────────▼───────────────────────┐
    │ Check Status Code                  │
    │ response.raise_for_status()        │
    └────────────┬───────────────────────┘
                 │
                 │ ✅ 2xx Success
                 ↓
    ┌────────────────────────────────────┐
    │ Parse Response                     │
    │ data = response.json()             │
    └────────────┬───────────────────────┘
                 │
    ┌────────────▼───────────────────────┐
    │ Update UI                          │
    │ st.success("Created!")             │
    │ st.rerun()                         │
    └────────────────────────────────────┘

except requests.exceptions.HTTPError as e:
    │
    ├─ 400 Bad Request
    │  ┌────────────────────────────────┐
    │  │ Validation Errors              │
    │  │ errors = e.response.json()     │
    │  │   ['errors']                   │
    │  │                                │
    │  │ for field, msgs in errors:     │
    │  │   st.error(f"{field}: {msgs}") │
    │  └────────────────────────────────┘
    │
    ├─ 401 Unauthorized
    │  ┌────────────────────────────────┐
    │  │ Token Invalid/Expired          │
    │  │ st.error("Please login again") │
    │  │ del st.session_state['token']  │
    │  │ st.rerun()                     │
    │  └────────────────────────────────┘
    │
    ├─ 403 Forbidden
    │  ┌────────────────────────────────┐
    │  │ Permission Denied              │
    │  │ st.error("Access denied")      │
    │  └────────────────────────────────┘
    │
    ├─ 404 Not Found
    │  ┌────────────────────────────────┐
    │  │ Resource Missing               │
    │  │ st.error("Article not found")  │
    │  └────────────────────────────────┘
    │
    └─ 500 Server Error
       ┌────────────────────────────────┐
       │ Backend Issue                  │
       │ st.error("Server error. Try    │
       │   again later")                │
       └────────────────────────────────┘

except requests.exceptions.ConnectionError:
    ┌────────────────────────────────────┐
    │ Backend Not Running                │
    │ st.error("Cannot connect to        │
    │   backend. Is it running?")        │
    │ st.code("python backend/app.py")   │
    └────────────────────────────────────┘

except requests.exceptions.Timeout:
    ┌────────────────────────────────────┐
    │ Request Took Too Long              │
    │ st.error("Request timeout")        │
    └────────────────────────────────────┘

except Exception as e:
    ┌────────────────────────────────────┐
    │ Unexpected Error                   │
    │ st.error(f"Unexpected: {e}")       │
    │ if st.checkbox("Show details"):    │
    │   st.exception(e)                  │
    └────────────────────────────────────┘


USER-FRIENDLY ERROR MESSAGES:
══════════════════════════════

❌ Bad:  "HTTPError: 400"
✅ Good: "Title must be at least 5 characters"

❌ Bad:  "ConnectionError"
✅ Good: "Cannot connect to backend. Make sure it's running on port 5000"

❌ Bad:  "Unauthorized"
✅ Good: "Your session has expired. Please login again."
```

---

## Usage During Teaching

### When to Draw Each Diagram:

1. **Diagram 1** - Start of chapter: Show full architecture
2. **Diagram 2** - Before first Streamlit demo: Explain rerun
3. **Diagram 3** - When implementing authentication
4. **Diagram 4** - When making first API call
5. **Diagram 5** - When introducing multi-page apps
6. **Diagram 6** - Before file upload exercise
7. **Diagram 7** - During Streamlit basics demo
8. **Diagram 8** - When building article listing
9. **Diagram 9** - When creating forms
10. **Diagram 10** - Before error handling section

**Teaching Tips:**
- Start with Diagram 1 to show the big picture
- Draw Diagram 2 live to explain reruns (most confusing concept!)
- Reference Diagram 7 as a cheat sheet
- Use Diagrams 3-6 when building Demo 2
- Keep diagrams simple during live coding

---

**Remember:** Streamlit's rerun behavior is the #1 source of confusion. Spend extra time on Diagram 2!
