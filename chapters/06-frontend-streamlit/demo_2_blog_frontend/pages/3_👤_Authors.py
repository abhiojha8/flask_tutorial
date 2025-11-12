"""
Authors Page
Browse all authors and view their profiles
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from config import API_BASE_URL
from utils.auth import init_session_state, is_authenticated
from utils.api_client import BlogAPIClient, handle_api_error

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Authors | Blog App",
    page_icon="👤",
    layout="wide"
)

# Initialize session state
init_session_state()

# ============================================================================
# VIEW MODE
# ============================================================================

# Check if viewing specific author profile
view_author_id = None
if 'selected_author_id' in st.session_state and st.session_state.selected_author_id:
    view_author_id = st.session_state.selected_author_id

# ============================================================================
# AUTHOR LIST VIEW
# ============================================================================

if not view_author_id:
    st.title("👤 Authors")
    st.caption("Meet our community of writers")

    st.divider()

    # Fetch all authors
    api = BlogAPIClient(API_BASE_URL)

    try:
        with st.spinner("Loading authors..."):
            response = api.get_authors()
            authors = response['authors']

        if authors:
            # Display authors in grid
            cols_per_row = 3
            rows = [authors[i:i + cols_per_row] for i in range(0, len(authors), cols_per_row)]

            for row in rows:
                cols = st.columns(cols_per_row)

                for idx, author in enumerate(row):
                    with cols[idx]:
                        with st.container():
                            st.subheader(f"👤 {author['name']}")
                            st.caption(f"✉️ {author['email']}")

                            # Stats
                            st.metric("📝 Articles", author['article_count'])

                            # View profile button
                            if st.button(f"View Profile", key=f"author_{author['id']}"):
                                st.session_state.selected_author_id = author['id']
                                st.rerun()

                            st.divider()

        else:
            st.info("📭 No authors found.")

    except Exception as e:
        handle_api_error(e)

# ============================================================================
# AUTHOR PROFILE VIEW
# ============================================================================

else:
    api = BlogAPIClient(API_BASE_URL)

    try:
        with st.spinner("Loading author profile..."):
            author = api.get_author(view_author_id)

        # Profile header
        st.title(f"👤 {author['name']}")
        st.caption(f"✉️ {author['email']}")

        st.divider()

        # Author stats
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📝 Total Articles", author['article_count'])

        with col2:
            total_views = sum(article['views'] for article in author.get('articles', []))
            st.metric("👁️ Total Views", total_views)

        with col3:
            total_comments = sum(article['comment_count'] for article in author.get('articles', []))
            st.metric("💬 Total Comments", total_comments)

        st.divider()

        # Author's articles
        st.header(f"📚 Articles by {author['name']}")

        articles = author.get('articles', [])

        if articles:
            # Filter controls
            col1, col2 = st.columns(2)

            with col1:
                show_drafts = st.checkbox(
                    "Show drafts",
                    value=False,
                    disabled=not is_authenticated() or st.session_state.user['id'] != author['id']
                )

            with col2:
                sort_by = st.selectbox(
                    "Sort by:",
                    options=["Newest", "Most Viewed", "Most Commented"]
                )

            # Filter articles
            if not show_drafts:
                articles = [a for a in articles if a['published']]

            # Sort articles
            if sort_by == "Newest":
                articles = sorted(articles, key=lambda x: x['created_at'], reverse=True)
            elif sort_by == "Most Viewed":
                articles = sorted(articles, key=lambda x: x['views'], reverse=True)
            elif sort_by == "Most Commented":
                articles = sorted(articles, key=lambda x: x['comment_count'], reverse=True)

            st.divider()

            # Display articles
            for article in articles:
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Title
                        st.subheader(f"📄 {article['title']}")

                        # Metadata
                        st.caption(f"{article['category'] or 'Uncategorized'} | {article['created_at'][:10]}")

                        # Content preview
                        content_preview = article['content'][:150] + "..." if len(article['content']) > 150 else article['content']
                        st.write(content_preview)

                        # Tags
                        if article.get('tags'):
                            tags_str = " ".join([f"`{tag}`" for tag in article['tags']])
                            st.markdown(f"🏷️ {tags_str}")

                    with col2:
                        # Metrics
                        st.metric("👁️ Views", article['views'])
                        st.metric("💬 Comments", article['comment_count'])

                        # Status
                        if article['published']:
                            st.success("Published ✅")
                        else:
                            st.warning("Draft 📝")

                        # View button
                        if st.button("Read →", key=f"read_{article['id']}"):
                            st.session_state.selected_author_id = None
                            st.switch_page("pages/1_📝_Articles.py")

                    st.divider()

        else:
            st.info("This author hasn't published any articles yet.")

            # Show message for own profile
            if is_authenticated() and st.session_state.user['id'] == author['id']:
                if st.button("✍️ Write Your First Article"):
                    st.session_state.selected_author_id = None
                    st.switch_page("pages/2_✍️_Create_Article.py")

    except Exception as e:
        handle_api_error(e)

    # Back button
    st.divider()

    if st.button("⬅️ Back to All Authors"):
        st.session_state.selected_author_id = None
        st.rerun()

# ============================================================================
# NAVIGATION
# ============================================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home"):
        st.session_state.selected_author_id = None
        st.switch_page("app.py")

with col2:
    if st.button("📝 View Articles"):
        st.session_state.selected_author_id = None
        st.switch_page("pages/1_📝_Articles.py")
