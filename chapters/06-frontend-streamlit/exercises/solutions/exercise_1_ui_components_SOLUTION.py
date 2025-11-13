"""
Exercise 1: Streamlit UI Components 🟢 - SOLUTION
Difficulty: Basic
Estimated Time: 30 minutes

This is the complete solution with all TODOs implemented.
"""

import streamlit as st
import requests

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

# TODO 1: SOLUTION
st.set_page_config(
    page_title="Exercise 1 | UI Components",
    page_icon="📝",
    layout="wide"
)

# ============================================================================
# PAGE HEADER
# ============================================================================

# TODO 2: SOLUTION
st.title("📝 Article Browser")
st.markdown("""
Welcome to the Article Browser! This app demonstrates how to use various Streamlit UI components
to display and filter articles from our backend API.

Use the filters below to search and filter articles.
""")

st.divider()

# ============================================================================
# FILTERS
# ============================================================================

st.subheader("🔍 Search & Filters")

# TODO 3: SOLUTION
col1, col2, col3 = st.columns(3)

with col1:
    # TODO 4: SOLUTION
    search_query = st.text_input(
        "Search articles:",
        placeholder="Enter keywords..."
    )

with col2:
    # TODO 5: SOLUTION
    category = st.selectbox(
        "Category:",
        ["All", "Technology", "Science", "Business", "Health", "Sports"]
    )

with col3:
    # TODO 6: SOLUTION
    published_only = st.checkbox("Published only", value=True)

st.divider()

# ============================================================================
# FETCH ARTICLES
# ============================================================================

# Fetch articles from API
try:
    response = requests.get(f"{API_BASE_URL}/articles", params={'per_page': 100}, timeout=5)
    response.raise_for_status()
    articles_data = response.json()
    articles = articles_data['articles']

    # Apply filters
    if search_query:
        articles = [a for a in articles if search_query.lower() in a['title'].lower()
                    or search_query.lower() in a['content'].lower()]

    if category != "All":
        articles = [a for a in articles if a.get('category') == category]

    if published_only:
        articles = [a for a in articles if a['published']]

except requests.exceptions.RequestException as e:
    st.error(f"❌ Error connecting to backend: {e}")
    st.info("Make sure the backend is running at http://localhost:5000")
    st.stop()

# ============================================================================
# STATISTICS
# ============================================================================

st.header("📊 Statistics")

# TODO 7: SOLUTION
col1, col2, col3, col4 = st.columns(4)

with col1:
    # TODO 8: SOLUTION
    st.metric("Total Articles", len(articles))

with col2:
    # TODO 9: SOLUTION
    published_count = len([a for a in articles if a['published']])
    st.metric("Published", published_count)

with col3:
    # TODO 10: SOLUTION
    draft_count = len([a for a in articles if not a['published']])
    st.metric("Drafts", draft_count)

with col4:
    # TODO 11: SOLUTION
    unique_categories = len(set(a.get('category') for a in articles if a.get('category')))
    st.metric("Categories", unique_categories)

st.divider()

# ============================================================================
# ARTICLE LIST
# ============================================================================

st.header("📚 Articles")

if articles:
    # TODO 12: SOLUTION
    for article in articles:
        # Create a container for this article
        with st.container():
            # TODO 13: SOLUTION
            col1, col2 = st.columns([3, 1])

            with col1:
                # TODO 14: SOLUTION
                st.subheader(f"📄 {article['title']}")

                # TODO 15: SOLUTION
                author_name = article['author']['name']
                article_category = article.get('category', 'Uncategorized')
                st.caption(f"By **{author_name}** | {article_category}")

                # TODO 16: SOLUTION
                content_preview = article['content'][:150]
                if len(article['content']) > 150:
                    content_preview += "..."
                st.write(content_preview)

                # TODO 17: SOLUTION
                if article.get('tags'):
                    tags_str = ' '.join([f"`{tag}`" for tag in article['tags']])
                    st.markdown(f"🏷️ {tags_str}")

            with col2:
                # TODO 18: SOLUTION
                st.metric("👁️ Views", article['views'])

                # TODO 19: SOLUTION
                st.metric("💬 Comments", article['comment_count'])

                # TODO 20: SOLUTION
                if article['published']:
                    st.success("✅ Published")
                else:
                    st.warning("📝 Draft")

            st.divider()
else:
    # TODO 21: SOLUTION
    st.info("📭 No articles found matching your filters.")

# ============================================================================
# SUMMARY
# ============================================================================

st.divider()

# TODO 22: SOLUTION
st.caption(f"""
**Summary:** Showing {len(articles)} article(s)
{f"| Search: '{search_query}'" if search_query else ""}
{f"| Category: {category}" if category != "All" else ""}
{f"| Status: Published only" if published_only else ""}
""")

# ============================================================================
# COMPLETION CHECK
# ============================================================================

st.divider()

st.success("""
✅ **Exercise 1 Complete!**

You've learned how to:
- Configure Streamlit pages
- Use various UI components
- Create layouts with columns
- Display metrics and statistics
- Format and organize content
- Add search and filter functionality

**Next Step:** Move on to Exercise 2 to learn API integration!
""")
