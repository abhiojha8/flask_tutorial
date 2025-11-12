"""
Demo 2: Full-Stack Blog Frontend
Chapter 6: Frontend Development with Streamlit

This is a complete blog application frontend that connects to the Flask backend.
Demonstrates:
- API integration
- Authentication flow
- CRUD operations
- File uploads
- Real-time updates
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from config import API_BASE_URL, APP_TITLE, APP_ICON, DEFAULT_PAGE_SIZE
from utils.auth import init_session_state, is_authenticated, show_user_info
from utils.api_client import BlogAPIClient, handle_api_error
import requests

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.divider()

    # Show user info
    show_user_info()

    st.divider()

    # Navigation helper
    st.subheader("📍 Navigation")
    st.markdown("""
    - **Home**: Browse articles
    - **Articles**: Detailed article view
    - **Create**: Write new article (login required)
    - **Authors**: View all authors
    - **Login**: Sign in or register
    """)

    st.divider()

    # Backend status check
    st.subheader("🔌 Backend Status")

    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/swagger", timeout=2)
        if response.status_code == 200:
            st.success("✅ Connected")
            st.caption(f"API: `{API_BASE_URL}`")
        else:
            st.warning("⚠️ Backend responding but may have issues")
    except:
        st.error("❌ Backend not connected")
        st.caption("Start backend:")
        st.code("cd backend && python app.py", language="bash")

# ============================================================================
# HOME PAGE
# ============================================================================

st.title("📝 Blog Home")

st.markdown("""
Welcome to the **Blog Application**! This is a full-stack demo showing Streamlit frontend
connected to Flask backend with authentication, CRUD operations, and file uploads.

**Features:**
- 🔐 User authentication with JWT
- 📝 Create, read, update, delete articles
- 💬 Comment system
- 🔍 Search and filter articles
- 📄 Pagination
- 🖼️ Image upload
- 👤 Author profiles
""")

st.divider()

# ============================================================================
# ARTICLE LISTING
# ============================================================================

st.header("📚 Recent Articles")

# Initialize session state for pagination and filters
if 'home_page' not in st.session_state:
    st.session_state.home_page = 1

if 'home_filters' not in st.session_state:
    st.session_state.home_filters = {}

# Filters
with st.expander("🔍 Search & Filters", expanded=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        search_query = st.text_input("Search articles:", placeholder="Enter keywords...")

    with col2:
        category_filter = st.selectbox(
            "Category:",
            ["All", "Technology", "Science", "Business", "Health", "Sports"]
        )

    with col3:
        published_filter = st.checkbox("Published only", value=True)

    if st.button("Apply Filters", type="primary"):
        st.session_state.home_filters = {
            'search': search_query if search_query else None,
            'category': category_filter if category_filter != "All" else None,
            'published': published_filter
        }
        st.session_state.home_page = 1  # Reset to first page
        st.rerun()

# Build query parameters
params = {
    'page': st.session_state.home_page,
    'per_page': DEFAULT_PAGE_SIZE,
    **st.session_state.home_filters
}

# Fetch articles
api = BlogAPIClient(API_BASE_URL)

with st.spinner("Loading articles..."):
    try:
        response = api.get_articles(params=params)
        articles = response['articles']
        pagination = response['pagination']

        if articles:
            # Display articles
            for article in articles:
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Title with link to detail page
                        st.subheader(f"📄 {article['title']}")

                        # Author and metadata
                        st.caption(f"By **{article['author']['name']}** | {article['category'] or 'Uncategorized'}")

                        # Content preview
                        content_preview = article['content'][:200] + "..." if len(article['content']) > 200 else article['content']
                        st.write(content_preview)

                        # Tags
                        if article.get('tags'):
                            tags_str = " ".join([f"`{tag}`" for tag in article['tags']])
                            st.markdown(f"🏷️ {tags_str}")

                    with col2:
                        # Metrics
                        st.metric("👁️ Views", article['views'])
                        st.metric("💬 Comments", article['comment_count'])

                        # Status badge
                        if article['published']:
                            st.success("Published ✅")
                        else:
                            st.warning("Draft 📝")

                    st.divider()

            # Pagination controls
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if st.session_state.home_page > 1:
                    if st.button("⬅️ Previous"):
                        st.session_state.home_page -= 1
                        st.rerun()

            with col2:
                st.write(f"**Page {pagination['page']} of {pagination['pages']}**")
                st.caption(f"Total articles: {pagination['total']}")

            with col3:
                if st.session_state.home_page < pagination['pages']:
                    if st.button("Next ➡️"):
                        st.session_state.home_page += 1
                        st.rerun()

        else:
            st.info("📭 No articles found. Be the first to create one!")

            if is_authenticated():
                if st.button("✍️ Create Article"):
                    st.switch_page("pages/2_✍️_Create_Article.py")

    except Exception as e:
        handle_api_error(e)

# ============================================================================
# QUICK STATS
# ============================================================================

st.divider()

st.header("📊 Quick Stats")

try:
    # Fetch all articles and authors for stats
    all_articles_response = api.get_articles(params={'per_page': 1000})
    authors_response = api.get_authors()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_articles = all_articles_response['pagination']['total']
        st.metric("Total Articles", total_articles)

    with col2:
        published_count = sum(1 for a in all_articles_response['articles'] if a['published'])
        st.metric("Published", published_count)

    with col3:
        total_views = sum(a['views'] for a in all_articles_response['articles'])
        st.metric("Total Views", total_views)

    with col4:
        total_authors = len(authors_response['authors'])
        st.metric("Authors", total_authors)

except Exception as e:
    st.caption("Could not load stats")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("""
---
**Blog Application** | Built with [Streamlit](https://streamlit.io/) + [Flask](https://flask.palletsprojects.com/)

**Chapter 6**: Frontend Development with Streamlit | Full-Stack Demo

💡 **Tip**: Use the sidebar to navigate between pages!
""")
