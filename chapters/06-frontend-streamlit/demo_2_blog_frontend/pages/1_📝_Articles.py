"""
Article Detail Page
Shows full article content with comments
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from config import API_BASE_URL
from utils.auth import init_session_state, is_authenticated, require_auth
from utils.api_client import BlogAPIClient, handle_api_error

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Articles | Blog App",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
init_session_state()

# ============================================================================
# ARTICLE SELECTION
# ============================================================================

st.title("📝 Articles")

api = BlogAPIClient(API_BASE_URL)

# Get all articles for selection
try:
    with st.spinner("Loading articles..."):
        response = api.get_articles(params={'per_page': 1000})
        all_articles = response['articles']

        if not all_articles:
            st.info("📭 No articles available yet.")
            if is_authenticated():
                if st.button("✍️ Create First Article"):
                    st.switch_page("pages/2_✍️_Create_Article.py")
            st.stop()

        # Article selector
        article_options = {
            f"{article['title']} (by {article['author']['name']})": article['id']
            for article in all_articles
        }

        selected_title = st.selectbox(
            "Select an article to view:",
            options=list(article_options.keys())
        )

        article_id = article_options[selected_title]

except Exception as e:
    handle_api_error(e)
    st.stop()

# ============================================================================
# ARTICLE DETAIL
# ============================================================================

try:
    # Fetch article details
    with st.spinner("Loading article..."):
        article = api.get_article(article_id)

    # Article header
    st.header(article['title'])

    # Metadata
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption(f"👤 By **{article['author']['name']}**")

    with col2:
        if article.get('category'):
            st.caption(f"🏷️ {article['category']}")

    with col3:
        if article['published']:
            st.caption("✅ Published")
        else:
            st.caption("📝 Draft")

    st.divider()

    # Article image (if exists)
    if article.get('image_url'):
        st.image(article['image_url'], use_container_width=True)

    # Article content
    st.markdown(article['content'])

    st.divider()

    # Tags
    if article.get('tags'):
        st.markdown("**Tags:**")
        tags_str = " ".join([f"`{tag}`" for tag in article['tags']])
        st.markdown(tags_str)

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("👁️ Views", article['views'])

    with col2:
        st.metric("💬 Comments", article['comment_count'])

    with col3:
        st.metric("📅 Created", article['created_at'][:10])

    st.divider()

    # Edit button (only for article owner)
    if is_authenticated() and st.session_state.user['id'] == article['author']['id']:
        if st.button("✏️ Edit Article"):
            st.session_state.edit_article_id = article_id
            st.switch_page("pages/2_✍️_Create_Article.py")

except Exception as e:
    handle_api_error(e)
    st.stop()

# ============================================================================
# COMMENTS SECTION
# ============================================================================

st.header("💬 Comments")

# Add comment form (authenticated users only)
if is_authenticated():
    with st.form("add_comment"):
        st.subheader("Add a Comment")
        comment_content = st.text_area(
            "Your comment:",
            placeholder="Share your thoughts...",
            height=100
        )

        submit_comment = st.form_submit_button("Post Comment", type="primary")

        if submit_comment:
            if not comment_content:
                st.error("❌ Comment cannot be empty!")
            else:
                try:
                    # Create comment
                    api = BlogAPIClient(API_BASE_URL, st.session_state.token)
                    new_comment = api.create_comment(article_id, {
                        'content': comment_content
                    })

                    st.success("✅ Comment posted successfully!")
                    st.rerun()

                except Exception as e:
                    handle_api_error(e)
else:
    st.info("🔐 Please log in to post comments")
    if st.button("Go to Login"):
        st.switch_page("pages/4_🔐_Login.py")

st.divider()

# Display comments
try:
    with st.spinner("Loading comments..."):
        comments_data = api.get_comments(article_id)
        comments = comments_data['comments']

    if comments:
        st.subheader(f"All Comments ({len(comments)})")

        for comment in comments:
            with st.container():
                # Comment header
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**{comment['author']['name']}**")
                    st.caption(f"{comment['created_at'][:10]} at {comment['created_at'][11:16]}")

                with col2:
                    # Delete button (only for comment owner or article owner)
                    if is_authenticated():
                        current_user_id = st.session_state.user['id']
                        is_comment_owner = current_user_id == comment['author']['id']
                        is_article_owner = current_user_id == article['author']['id']

                        if is_comment_owner or is_article_owner:
                            if st.button("🗑️", key=f"delete_{comment['id']}"):
                                try:
                                    api_auth = BlogAPIClient(API_BASE_URL, st.session_state.token)
                                    api_auth.delete_comment(article_id, comment['id'])
                                    st.success("✅ Comment deleted!")
                                    st.rerun()
                                except Exception as e:
                                    handle_api_error(e)

                # Comment content
                st.write(comment['content'])

                st.divider()
    else:
        st.info("No comments yet. Be the first to comment!")

except Exception as e:
    handle_api_error(e)

# ============================================================================
# NAVIGATION
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")

with col2:
    if st.button("👤 View Author Profile"):
        st.session_state.selected_author_id = article['author']['id']
        st.switch_page("pages/3_👤_Authors.py")

with col3:
    if is_authenticated():
        if st.button("✍️ Write Article"):
            st.switch_page("pages/2_✍️_Create_Article.py")
