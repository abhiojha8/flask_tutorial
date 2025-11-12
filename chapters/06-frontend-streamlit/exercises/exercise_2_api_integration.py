"""
Exercise 2: API Integration 🟢
Difficulty: Basic
Estimated Time: 45 minutes

SOLUTION
"""

import streamlit as st
import requests
from typing import Dict, Optional, List
import time

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# API CLIENT CLASS
# ============================================================================

class ArticleAPIClient:
    """API client for interacting with the blog backend."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    # SOLUTION 1: get_articles method
    def get_articles(self, params: Optional[Dict] = None) -> Dict:
        """Fetch articles from API."""
        response = requests.get(
            f"{self.base_url}/articles",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 2: get_article method
    def get_article(self, article_id: int) -> Dict:
        """Fetch a single article by ID."""
        response = requests.get(
            f"{self.base_url}/articles/{article_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 3: get_authors method
    def get_authors(self) -> Dict:
        """Fetch all authors."""
        response = requests.get(
            f"{self.base_url}/authors",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

# ============================================================================
# ERROR HANDLING HELPER
# ============================================================================

# SOLUTION 4: handle_api_error function
def handle_api_error(error: Exception):
    """Display user-friendly error messages for API errors."""
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("❌ Cannot connect to backend server")
        st.info("Please ensure the backend is running at http://localhost:5000")
    elif isinstance(error, requests.exceptions.Timeout):
        st.warning("⏱️ Request timed out. The server may be slow or unavailable.")
    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = error.response.status_code
        if status_code == 400:
            st.error("❌ Bad request - Invalid parameters")
        elif status_code == 401:
            st.error("🔒 Unauthorized - Please login")
        elif status_code == 403:
            st.error("⛔ Forbidden - You don't have permission")
        elif status_code == 404:
            st.error("🔍 Not found - Resource doesn't exist")
        elif status_code >= 500:
            st.error("💥 Server error - Please try again later")
        else:
            st.error(f"❌ HTTP Error {status_code}")
    else:
        st.error(f"❌ Unexpected error: {str(error)}")

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Exercise 2 | API Integration",
    page_icon="🔌",
    layout="wide"
)

# ============================================================================
# HEADER
# ============================================================================

st.title("🔌 API Integration")
st.markdown("""
This app demonstrates proper API integration with error handling and loading states.
""")

st.divider()

# ============================================================================
# BACKEND STATUS CHECK
# ============================================================================

st.subheader("🔌 Backend Status")

# SOLUTION 5: Backend status check
try:
    response = requests.get(API_BASE_URL.replace('/api', '/swagger'), timeout=2)
    if response.status_code == 200:
        st.success("✅ Backend is connected and running!")
        st.caption(f"API URL: `{API_BASE_URL}`")
    else:
        st.warning("⚠️ Backend responded but may have issues")
except requests.exceptions.RequestException:
    st.error("❌ Backend is not connected")
    st.code("cd backend && python app.py", language="bash")

st.divider()

# ============================================================================
# INITIALIZE API CLIENT
# ============================================================================

# SOLUTION 6: Create API client instance
api = ArticleAPIClient(API_BASE_URL)

# ============================================================================
# PAGINATION STATE
# ============================================================================

# SOLUTION 7: Initialize pagination state
if 'page' not in st.session_state:
    st.session_state.page = 1

# ============================================================================
# FETCH ARTICLES
# ============================================================================

st.header("📚 Articles")

# SOLUTION 8: Fetch articles with error handling
try:
    with st.spinner("Loading articles..."):
        response = api.get_articles(params={
            'page': st.session_state.page,
            'per_page': 5
        })

        articles = response['articles']
        pagination = response['pagination']

except Exception as e:
    handle_api_error(e)
    st.stop()

# ============================================================================
# DISPLAY ARTICLES
# ============================================================================

# SOLUTION 9: Display articles
if articles:
    for article in articles:
        with st.container():
            st.subheader(f"📄 {article['title']}")
            st.caption(f"By {article['author']['name']} | {article.get('category', 'Uncategorized')}")

            content_preview = article['content'][:200] + "..." if len(article['content']) > 200 else article['content']
            st.write(content_preview)

            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"👁️ {article['views']} views")
            with col2:
                st.caption(f"💬 {article['comment_count']} comments")

            st.divider()
else:
    st.info("📭 No articles found.")

# ============================================================================
# PAGINATION CONTROLS
# ============================================================================

st.divider()

# SOLUTION 10: Pagination controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.page > 1:
        if st.button("⬅️ Previous"):
            st.session_state.page -= 1
            st.rerun()

with col2:
    st.write(f"**Page {pagination['page']} of {pagination['pages']}**")
    st.caption(f"Total: {pagination['total']} articles")

with col3:
    if st.session_state.page < pagination['pages']:
        if st.button("Next ➡️"):
            st.session_state.page += 1
            st.rerun()

# ============================================================================
# DETAILED ARTICLE VIEW
# ============================================================================

st.divider()
st.header("🔍 View Article Details")

# SOLUTION 11: Article detail viewer
article_id = st.number_input("Enter Article ID:", min_value=1, step=1, value=1)

if st.button("Load Article"):
    try:
        with st.spinner(f"Loading article {article_id}..."):
            article = api.get_article(article_id)

        st.success("✅ Article loaded!")

        st.subheader(article['title'])
        st.caption(f"By **{article['author']['name']}** | {article.get('category', 'Uncategorized')}")
        st.markdown(article['content'])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Views", article['views'])
        with col2:
            st.metric("Comments", article['comment_count'])
        with col3:
            status = "Published ✅" if article['published'] else "Draft 📝"
            st.metric("Status", status)

    except Exception as e:
        handle_api_error(e)

# ============================================================================
# AUTHORS SECTION
# ============================================================================

st.divider()
st.header("👤 Authors")

# SOLUTION 12: Fetch and display authors
if st.button("Load Authors"):
    try:
        with st.spinner("Loading authors..."):
            response = api.get_authors()
            authors = response['authors']

        st.success(f"✅ Loaded {len(authors)} authors!")

        # Display in grid
        cols = st.columns(3)
        for idx, author in enumerate(authors):
            with cols[idx % 3]:
                st.subheader(f"👤 {author['name']}")
                st.caption(author['email'])
                st.metric("Articles", author['article_count'])
                st.divider()

    except Exception as e:
        handle_api_error(e)

# ============================================================================
# RETRY MECHANISM
# ============================================================================

st.divider()
st.header("🔄 Retry Logic")

st.markdown("""
Sometimes API calls fail due to temporary network issues. Let's implement retry logic.
""")

# SOLUTION 13: Retry mechanism
def retry_api_call(func, max_attempts=3):
    """Retry an API call multiple times if it fails."""
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            st.info(f"Attempt {attempt} of {max_attempts}...")
            result = func()
            st.success(f"✅ Success on attempt {attempt}!")
            return result
        except Exception as e:
            last_exception = e
            st.warning(f"⚠️ Attempt {attempt} failed: {str(e)}")
            if attempt < max_attempts:
                st.info("Retrying in 1 second...")
                time.sleep(1)

    # All attempts failed
    st.error(f"❌ All {max_attempts} attempts failed")
    raise last_exception

# Test retry logic
if st.button("Test Retry Logic"):
    try:
        def fetch_articles():
            return api.get_articles(params={'page': 1, 'per_page': 3})

        with st.spinner("Testing retry mechanism..."):
            result = retry_api_call(fetch_articles, max_attempts=3)

        st.write(f"Successfully fetched {len(result['articles'])} articles!")

    except Exception as e:
        handle_api_error(e)

# ============================================================================
# COMPLETION CHECK
# ============================================================================

st.divider()

st.success("""
✅ **Exercise 2 Complete!**

You've learned how to:
- Create an API client class
- Make HTTP requests properly
- Handle errors gracefully
- Show loading states
- Implement pagination
- Add retry logic for reliability

**Next Step:** Move on to Exercise 3 to learn authentication!
""")

# ============================================================================
# TESTING CHECKLIST
# ============================================================================

with st.expander("✅ Testing Checklist"):
    st.markdown("""
    Test your implementation:

    **With Backend Running:**
    - [x] Articles load successfully
    - [x] Pagination works (next/previous)
    - [x] Article detail viewer works
    - [x] Authors load successfully
    - [x] Loading spinners appear

    **With Backend Stopped:**
    - [x] Connection error message appears
    - [x] Error messages are user-friendly
    - [x] App doesn't crash
    - [x] Retry logic shows attempts

    **Edge Cases:**
    - [x] Invalid article ID shows proper error
    - [x] Empty results handled gracefully
    - [x] Timeout errors handled
    """)
