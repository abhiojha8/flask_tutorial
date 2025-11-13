"""
Exercise 2: API Integration 🟢 - SOLUTION
Difficulty: Basic
Estimated Time: 45 minutes

This is the complete solution with all TODOs implemented.
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

    # TODO 1: SOLUTION
    def get_articles(self, params: Optional[Dict] = None) -> Dict:
        """Fetch articles from API."""
        response = requests.get(f"{self.base_url}/articles", params=params, timeout=5)
        response.raise_for_status()
        return response.json()

    # TODO 2: SOLUTION
    def get_article(self, article_id: int) -> Dict:
        """Fetch a single article by ID."""
        response = requests.get(f"{self.base_url}/articles/{article_id}", timeout=5)
        response.raise_for_status()
        return response.json()

    # TODO 3: SOLUTION
    def get_authors(self) -> Dict:
        """Fetch all authors."""
        response = requests.get(f"{self.base_url}/authors", timeout=5)
        response.raise_for_status()
        return response.json()

# ============================================================================
# ERROR HANDLING HELPER
# ============================================================================

# TODO 4: SOLUTION
def handle_api_error(error: Exception):
    """Display user-friendly error messages for API errors."""
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("❌ Cannot connect to backend API")
        st.info("Make sure the Flask backend is running:")
        st.code("cd backend && python app.py", language="bash")

    elif isinstance(error, requests.exceptions.Timeout):
        st.error("⏱️ Request timeout - Backend is taking too long to respond")

    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = error.response.status_code

        if status_code == 400:
            st.error(f"❌ Bad request: {error.response.text}")
        elif status_code == 404:
            st.error("🔍 Resource not found")
        elif status_code >= 500:
            st.error("🔥 Server error - Something went wrong on the backend")
        else:
            st.error(f"❌ Error: HTTP {status_code}")

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

# TODO 5: SOLUTION
try:
    response = requests.get("http://localhost:5000", timeout=2)
    st.success("✅ Backend is running!")
except requests.exceptions.Timeout:
    st.error("❌ Backend timeout - taking too long to respond")
except requests.exceptions.ConnectionError:
    st.error("❌ Backend is not running")
    st.info("Start the backend with: `cd backend && python app.py`")
except Exception as e:
    st.warning(f"⚠️ Cannot reach backend: {e}")

st.divider()

# ============================================================================
# INITIALIZE API CLIENT
# ============================================================================

# TODO 6: SOLUTION
api = ArticleAPIClient(API_BASE_URL)

# ============================================================================
# PAGINATION STATE
# ============================================================================

# TODO 7: SOLUTION
if 'page' not in st.session_state:
    st.session_state.page = 1

# ============================================================================
# FETCH ARTICLES
# ============================================================================

st.header("📚 Articles")

# TODO 8: SOLUTION
articles = []
pagination = {}

try:
    with st.spinner("Loading articles..."):
        response = api.get_articles({'page': st.session_state.page, 'per_page': 5})
        articles = response.get('articles', [])
        pagination = response.get('pagination', {})
except Exception as e:
    handle_api_error(e)
    st.stop()

# ============================================================================
# DISPLAY ARTICLES
# ============================================================================

# TODO 9: SOLUTION
if articles:
    for article in articles:
        with st.container():
            st.subheader(f"📄 {article['title']}")
            st.caption(f"By **{article['author']['name']}** | {article.get('category', 'Uncategorized')}")

            content_preview = article['content'][:200]
            if len(article['content']) > 200:
                content_preview += "..."
            st.write(content_preview)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Views", article['views'])
            with col2:
                st.metric("Comments", article['comment_count'])
            with col3:
                status = "✅ Published" if article['published'] else "📝 Draft"
                st.write(status)

            st.divider()
else:
    st.info("📭 No articles found")

# ============================================================================
# PAGINATION CONTROLS
# ============================================================================

st.divider()

# TODO 10: SOLUTION
if pagination:
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.page > 1:
            if st.button("⬅️ Previous"):
                st.session_state.page -= 1
                st.rerun()

    with col2:
        st.write(f"Page {pagination.get('page', 1)} of {pagination.get('pages', 1)}")

    with col3:
        if st.session_state.page < pagination.get('pages', 1):
            if st.button("Next ➡️"):
                st.session_state.page += 1
                st.rerun()

# ============================================================================
# DETAILED ARTICLE VIEW
# ============================================================================

st.divider()
st.header("🔍 View Article Details")

# TODO 11: SOLUTION
article_id = st.number_input("Article ID", min_value=1, value=1, step=1)

if st.button("Load Article"):
    try:
        with st.spinner(f"Loading article {article_id}..."):
            article = api.get_article(article_id)

        st.success(f"✅ Loaded: {article['title']}")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(article['title'])
            st.caption(f"By **{article['author']['name']}** | {article.get('category', 'Uncategorized')}")
            st.write(article['content'])

            if article.get('tags'):
                tags_str = ' '.join([f"`{tag}`" for tag in article['tags']])
                st.markdown(f"🏷️ {tags_str}")

        with col2:
            st.metric("Views", article['views'])
            st.metric("Comments", article['comment_count'])

            if article['published']:
                st.success("✅ Published")
            else:
                st.warning("📝 Draft")

            st.caption(f"Created: {article['created_at'][:10]}")

    except Exception as e:
        handle_api_error(e)

# ============================================================================
# AUTHORS SECTION
# ============================================================================

st.divider()
st.header("👤 Authors")

# TODO 12: SOLUTION
if st.button("Load Authors"):
    try:
        with st.spinner("Loading authors..."):
            response = api.get_authors()
            authors = response.get('authors', [])

        st.success(f"✅ Loaded {len(authors)} authors")

        cols = st.columns(3)

        for idx, author in enumerate(authors):
            with cols[idx % 3]:
                with st.container():
                    st.subheader(f"👤 {author['name']}")
                    st.caption(author['email'])
                    st.metric("Articles", author.get('article_count', 0))

                    if author.get('bio'):
                        st.write(author['bio'])

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

# TODO 13: SOLUTION
def retry_api_call(func, max_attempts=3):
    """Retry an API call multiple times if it fails."""
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            st.info(f"Attempt {attempt} of {max_attempts}...")
            result = func()
            st.success(f"✅ Success on attempt {attempt}!")
            return result
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                st.warning(f"⚠️ Attempt {attempt} failed, retrying...")
                time.sleep(1)
            else:
                st.error(f"❌ All {max_attempts} attempts failed")

    raise last_error

# Test retry logic
if st.button("Test Retry Logic"):
    try:
        result = retry_api_call(lambda: api.get_articles({'per_page': 5}))
        st.json({"articles_fetched": len(result.get('articles', []))})
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
    - [ ] Articles load successfully
    - [ ] Pagination works (next/previous)
    - [ ] Article detail viewer works
    - [ ] Authors load successfully
    - [ ] Loading spinners appear

    **With Backend Stopped:**
    - [ ] Connection error message appears
    - [ ] Error messages are user-friendly
    - [ ] App doesn't crash
    - [ ] Retry logic shows attempts

    **Edge Cases:**
    - [ ] Invalid article ID shows proper error
    - [ ] Empty results handled gracefully
    - [ ] Timeout errors handled
    """)
