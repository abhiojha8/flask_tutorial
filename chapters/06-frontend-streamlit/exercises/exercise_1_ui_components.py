"""
Exercise 1: Streamlit UI Components 🟢
Difficulty: Basic
Estimated Time: 30 minutes

GOAL:
Build a simple Streamlit app that displays article information using various UI components.

LEARNING OBJECTIVES:
- Use Streamlit basic components (title, header, text, metrics)
- Create layouts with columns
- Display data in organized format
- Add user input widgets (search, filters)

REQUIREMENTS:
1. Display a title and description
2. Show article statistics using metrics
3. Use columns for layout
4. Add search/filter functionality
5. Display article list with formatting

INSTRUCTIONS:
1. Look for TODO comments
2. Implement the required functionality
3. Run: streamlit run exercise_1_ui_components.py
4. Test your implementation

HINTS:
- Use st.title() for main title
- Use st.columns() for side-by-side layout
- Use st.metric() to display statistics
- Use st.text_input() for search
- Use st.selectbox() for filters
"""

import streamlit as st
import requests

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

# TODO 1: Configure the page with title, icon, and wide layout
# Hint: Use st.set_page_config()
# - page_title: "Exercise 1 | UI Components"
# - page_icon: "📝"
# - layout: "wide"

# YOUR CODE HERE


# ============================================================================
# PAGE HEADER
# ============================================================================

# TODO 2: Add a title and description
# Hint: Use st.title() and st.markdown()
# Title: "📝 Article Browser"
# Description: Welcome message explaining what the app does

# YOUR CODE HERE


st.divider()

# ============================================================================
# FILTERS
# ============================================================================

st.subheader("🔍 Search & Filters")

# TODO 3: Create a 3-column layout for filters
# Hint: Use st.columns(3)
# col1: Search text input
# col2: Category selectbox
# col3: Published checkbox

# YOUR CODE HERE
col1, col2, col3 = st.columns(3)

with col1:
    # TODO 4: Add a text input for search
    # Hint: Use st.text_input()
    # Label: "Search articles:"
    # Placeholder: "Enter keywords..."

    # YOUR CODE HERE
    search_query = ""  # Replace with actual text input

with col2:
    # TODO 5: Add a selectbox for category filter
    # Hint: Use st.selectbox()
    # Label: "Category:"
    # Options: ["All", "Technology", "Science", "Business", "Health", "Sports"]

    # YOUR CODE HERE
    category = "All"  # Replace with actual selectbox

with col3:
    # TODO 6: Add a checkbox for published filter
    # Hint: Use st.checkbox()
    # Label: "Published only"
    # Default: True

    # YOUR CODE HERE
    published_only = True  # Replace with actual checkbox

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

# TODO 7: Create a 4-column layout for metrics
# Hint: Use st.columns(4)
# Display metrics for: Total Articles, Published, Drafts, Categories

# YOUR CODE HERE
col1, col2, col3, col4 = st.columns(4)

with col1:
    # TODO 8: Display total articles count
    # Hint: Use st.metric()
    # Label: "Total Articles"
    # Value: len(articles)

    # YOUR CODE HERE
    pass

with col2:
    # TODO 9: Display published articles count
    # Hint: Use st.metric() and count articles where published=True
    # Label: "Published"

    # YOUR CODE HERE
    pass

with col3:
    # TODO 10: Display draft articles count
    # Hint: Use st.metric() and count articles where published=False
    # Label: "Drafts"

    # YOUR CODE HERE
    pass

with col4:
    # TODO 11: Display unique categories count
    # Hint: Use st.metric() and count unique categories
    # Label: "Categories"

    # YOUR CODE HERE
    pass

st.divider()

# ============================================================================
# ARTICLE LIST
# ============================================================================

st.header("📚 Articles")

if articles:
    # TODO 12: Loop through articles and display each one
    # For each article, create a container with:
    # - Title as subheader
    # - Author name and category as caption
    # - Content preview (first 150 characters)
    # - Metrics in columns (views, comments)
    # - Status badge (Published or Draft)
    # - Divider between articles

    # Hint: Use a for loop
    # Hint: Use st.container() for each article
    # Hint: Use st.columns([3, 1]) for layout

    # YOUR CODE HERE
    for article in articles:
        # Create a container for this article
        with st.container():
            # TODO 13: Create 2 columns with ratio [3, 1]
            # Left column (col1): Article content
            # Right column (col2): Metrics and status

            # YOUR CODE HERE
            col1, col2 = st.columns([3, 1])

            with col1:
                # TODO 14: Display article title as subheader
                # Hint: st.subheader(f"📄 {article['title']}")

                # YOUR CODE HERE
                pass

                # TODO 15: Display author and category as caption
                # Hint: st.caption(f"By **{article['author']['name']}** | {category}")

                # YOUR CODE HERE
                pass

                # TODO 16: Display content preview (first 150 chars)
                # Hint: Use slicing and add "..." if content is long

                # YOUR CODE HERE
                pass

                # TODO 17: Display tags if they exist
                # Hint: Check if article has 'tags'
                # Hint: Format as: 🏷️ `tag1` `tag2` `tag3`

                # YOUR CODE HERE
                pass

            with col2:
                # TODO 18: Display views metric
                # Hint: st.metric("👁️ Views", article['views'])

                # YOUR CODE HERE
                pass

                # TODO 19: Display comments count metric
                # Hint: st.metric("💬 Comments", article['comment_count'])

                # YOUR CODE HERE
                pass

                # TODO 20: Display status badge
                # Hint: Use st.success() for published, st.warning() for draft

                # YOUR CODE HERE
                pass

            st.divider()
else:
    # TODO 21: Display a message when no articles found
    # Hint: Use st.info()
    # Message: "📭 No articles found matching your filters."

    # YOUR CODE HERE
    pass

# ============================================================================
# SUMMARY
# ============================================================================

st.divider()

# TODO 22: Display a summary section
# Show:
# - Total articles found
# - Filters applied (if any)
# Hint: Use st.caption() or st.markdown()

# YOUR CODE HERE


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
