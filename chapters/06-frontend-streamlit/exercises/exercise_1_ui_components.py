"""
Exercise 1: Streamlit UI Components 🟢
Difficulty: Basic
Estimated Time: 30 minutes

SOLUTION
"""

import streamlit as st
import requests

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

# SOLUTION 1: Configure the page
st.set_page_config(
    page_title="Exercise 1 | UI Components",
    page_icon="📝",
    layout="wide"
)

# ============================================================================
# PAGE HEADER
# ============================================================================

# SOLUTION 2: Add title and description
st.title("📝 Article Browser")
st.markdown("""
Welcome to the **Article Browser**! This app demonstrates Streamlit UI components
by displaying articles from our blog API.

Browse articles, search by keywords, filter by category, and explore the data!
""")

st.divider()

# ============================================================================
# FILTERS
# ============================================================================

st.subheader("🔍 Search & Filters")

# SOLUTION 3: Create 3-column layout
col1, col2, col3 = st.columns(3)

with col1:
    # SOLUTION 4: Text input for search
    search_query = st.text_input(
        "Search articles:",
        placeholder="Enter keywords..."
    )

with col2:
    # SOLUTION 5: Selectbox for category
    category = st.selectbox(
        "Category:",
        ["All", "Technology", "Science", "Business", "Health", "Sports"]
    )

with col3:
    # SOLUTION 6: Checkbox for published filter
    published_only = st.checkbox("Published only", value=True)

st.divider()

# ============================================================================
# FETCH ARTICLES
# ============================================================================

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

# SOLUTION 7: Create 4-column layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    # SOLUTION 8: Total articles metric
    st.metric("Total Articles", len(articles))

with col2:
    # SOLUTION 9: Published count
    published_count = sum(1 for a in articles if a['published'])
    st.metric("Published", published_count)

with col3:
    # SOLUTION 10: Draft count
    draft_count = sum(1 for a in articles if not a['published'])
    st.metric("Drafts", draft_count)

with col4:
    # SOLUTION 11: Unique categories count
    unique_categories = len(set(a.get('category') for a in articles if a.get('category')))
    st.metric("Categories", unique_categories)

st.divider()

# ============================================================================
# ARTICLE LIST
# ============================================================================

st.header("📚 Articles")

if articles:
    # SOLUTION 12: Loop through articles
    for article in articles:
        with st.container():
            # SOLUTION 13: Create 2 columns
            col1, col2 = st.columns([3, 1])

            with col1:
                # SOLUTION 14: Display title
                st.subheader(f"📄 {article['title']}")

                # SOLUTION 15: Display author and category
                category_text = article.get('category') or 'Uncategorized'
                st.caption(f"By **{article['author']['name']}** | {category_text}")

                # SOLUTION 16: Content preview
                content = article['content']
                if len(content) > 150:
                    content_preview = content[:150] + "..."
                else:
                    content_preview = content
                st.write(content_preview)

                # SOLUTION 17: Display tags
                if article.get('tags'):
                    tags_str = " ".join([f"`{tag}`" for tag in article['tags']])
                    st.markdown(f"🏷️ {tags_str}")

            with col2:
                # SOLUTION 18: Views metric
                st.metric("👁️ Views", article['views'])

                # SOLUTION 19: Comments metric
                st.metric("💬 Comments", article['comment_count'])

                # SOLUTION 20: Status badge
                if article['published']:
                    st.success("Published ✅")
                else:
                    st.warning("Draft 📝")

            st.divider()
else:
    # SOLUTION 21: No articles message
    st.info("📭 No articles found matching your filters.")

# ============================================================================
# SUMMARY
# ============================================================================

st.divider()

# SOLUTION 22: Display summary
st.caption(f"Showing {len(articles)} article(s)")

if search_query or category != "All" or not published_only:
    st.caption("**Active filters:**")
    filters_applied = []
    if search_query:
        filters_applied.append(f"Search: '{search_query}'")
    if category != "All":
        filters_applied.append(f"Category: {category}")
    if not published_only:
        filters_applied.append("Including drafts")

    for filter_text in filters_applied:
        st.caption(f"- {filter_text}")

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
