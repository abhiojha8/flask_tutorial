"""
Exercise 2: API Integration 🟢
Difficulty: Basic
Estimated Time: 45 minutes

GOAL:
Create an app that properly integrates with the Flask backend API, including
error handling, loading states, and data processing.

LEARNING OBJECTIVES:
- Make HTTP requests to REST API
- Handle API responses and errors
- Show loading states
- Process and display API data
- Implement retry logic

REQUIREMENTS:
1. Create an API client class
2. Fetch articles from backend
3. Handle connection errors
4. Show loading spinners
5. Display data with pagination
6. Implement retry logic

INSTRUCTIONS:
1. Look for TODO comments
2. Implement the required functionality
3. Run: streamlit run exercise_2_api_integration.py
4. Test with backend running and stopped

HINTS:
- Use requests library for HTTP calls
- Use st.spinner() for loading states
- Use try/except for error handling
- Check response.status_code
- Parse JSON with response.json()
"""

import streamlit as st
import requests
from typing import Dict, Optional, List

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# API CLIENT CLASS
# ============================================================================

class ArticleAPIClient:
    """
    API client for interacting with the blog backend.
    Handles all HTTP requests and error handling.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    # TODO 1: Implement get_articles method
    # This method should:
    # - Accept optional params dict (page, per_page, etc.)
    # - Make GET request to /articles endpoint
    # - Raise HTTPError for bad status codes
    # - Return the JSON response
    #
    # Hint: Use requests.get()
    # Hint: Use response.raise_for_status()
    # Hint: Return response.json()

    def get_articles(self, params: Optional[Dict] = None) -> Dict:
        """
        Fetch articles from API.

        Args:
            params: Query parameters (page, per_page, search, etc.)

        Returns:
            Dictionary containing articles and pagination info

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        # YOUR CODE HERE
        pass

    # TODO 2: Implement get_article method
    # This method should:
    # - Accept article_id parameter
    # - Make GET request to /articles/{article_id}
    # - Handle errors
    # - Return the article data
    #
    # Hint: URL should be f"{self.base_url}/articles/{article_id}"

    def get_article(self, article_id: int) -> Dict:
        """
        Fetch a single article by ID.

        Args:
            article_id: The article ID

        Returns:
            Dictionary containing article data

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        # YOUR CODE HERE
        pass

    # TODO 3: Implement get_authors method
    # This method should:
    # - Make GET request to /authors endpoint
    # - Return the JSON response
    #
    # Hint: Similar to get_articles but different endpoint

    def get_authors(self) -> Dict:
        """
        Fetch all authors.

        Returns:
            Dictionary containing authors list

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        # YOUR CODE HERE
        pass

# ============================================================================
# ERROR HANDLING HELPER
# ============================================================================

# TODO 4: Implement handle_api_error function
# This function should:
# - Accept an exception as parameter
# - Check the exception type
# - Display appropriate error message
# - Handle: ConnectionError, Timeout, HTTPError (with status codes)
#
# Hint: Use isinstance() to check exception type
# Hint: Use st.error() for errors, st.warning() for warnings

def handle_api_error(error: Exception):
    """
    Display user-friendly error messages for API errors.

    Args:
        error: The exception that occurred
    """
    # YOUR CODE HERE
    pass

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

# TODO 5: Implement backend status check
# This should:
# - Try to connect to the backend
# - Show success message if connected
# - Show error message if not connected
# - Use a timeout of 2 seconds
#
# Hint: Make a request to base URL (without /api)
# Hint: Use try/except with requests.Timeout
# Hint: Use st.success() or st.error()

# YOUR CODE HERE


st.divider()

# ============================================================================
# INITIALIZE API CLIENT
# ============================================================================

# TODO 6: Create an instance of ArticleAPIClient
# Hint: api = ArticleAPIClient(API_BASE_URL)

# YOUR CODE HERE
api = None  # Replace with actual client instance

# ============================================================================
# PAGINATION STATE
# ============================================================================

# TODO 7: Initialize session state for pagination
# Create session state variable 'page' with default value 1
# Hint: Check if 'page' not in st.session_state, then set it

# YOUR CODE HERE


# ============================================================================
# FETCH ARTICLES
# ============================================================================

st.header("📚 Articles")

# TODO 8: Fetch articles with loading spinner and error handling
# This should:
# - Show a loading spinner with message "Loading articles..."
# - Try to fetch articles using api.get_articles()
# - Pass params for pagination: {'page': st.session_state.page, 'per_page': 5}
# - Store articles and pagination in variables
# - Handle errors using handle_api_error()
# - Stop execution if error occurs
#
# Hint: Use with st.spinner("message"):
# Hint: Use try/except
# Hint: Use st.stop() to halt execution on error

# YOUR CODE HERE
try:
    with st.spinner("Loading articles..."):
        # Fetch articles
        pass
except Exception as e:
    # Handle error
    pass

# ============================================================================
# DISPLAY ARTICLES
# ============================================================================

# TODO 9: Display articles or "no articles" message
# If articles exist:
# - Loop through and display each article
# - Show title, author, content preview
# - Add divider between articles
# If no articles:
# - Show info message

# YOUR CODE HERE


# ============================================================================
# PAGINATION CONTROLS
# ============================================================================

st.divider()

# TODO 10: Implement pagination controls
# Create 3 columns
# col1: Previous button (only if page > 1)
# col2: Page info (current page / total pages)
# col3: Next button (only if page < total pages)
#
# Hint: Use st.columns(3)
# Hint: Check st.session_state.page for current page
# Hint: Use pagination['pages'] for total pages
# Hint: On button click, update st.session_state.page and st.rerun()

# YOUR CODE HERE


# ============================================================================
# DETAILED ARTICLE VIEW
# ============================================================================

st.divider()
st.header("🔍 View Article Details")

# TODO 11: Implement article detail viewer
# - Create a number input for article ID
# - Add a button "Load Article"
# - When clicked:
#   - Show loading spinner
#   - Fetch article using api.get_article()
#   - Display full article details
#   - Handle errors
#
# Hint: Use st.number_input() with min_value=1
# Hint: Use st.button()
# Hint: Display title, author, content, stats

# YOUR CODE HERE


# ============================================================================
# AUTHORS SECTION
# ============================================================================

st.divider()
st.header("👤 Authors")

# TODO 12: Fetch and display authors
# - Add a button "Load Authors"
# - When clicked:
#   - Show loading spinner
#   - Fetch authors using api.get_authors()
#   - Display authors in columns
#   - Show author name, email, article count
#   - Handle errors
#
# Hint: Similar pattern to articles
# Hint: Use st.columns() for grid layout

# YOUR CODE HERE


# ============================================================================
# RETRY MECHANISM
# ============================================================================

st.divider()
st.header("🔄 Retry Logic")

st.markdown("""
Sometimes API calls fail due to temporary network issues. Let's implement retry logic.
""")

# TODO 13: Implement a retry mechanism
# Create a function that:
# - Accepts a function to retry and max_attempts
# - Tries the function up to max_attempts times
# - Waits 1 second between retries
# - Returns result if successful
# - Raises exception if all attempts fail
#
# Hint: Use a for loop
# Hint: Use time.sleep(1) between attempts
# Hint: Use try/except inside the loop

import time

def retry_api_call(func, max_attempts=3):
    """
    Retry an API call multiple times if it fails.

    Args:
        func: Function to retry (should take no arguments)
        max_attempts: Maximum number of attempts

    Returns:
        Result of the function if successful

    Raises:
        Last exception if all attempts fail
    """
    # YOUR CODE HERE
    pass

# Test retry logic
if st.button("Test Retry Logic"):
    # YOUR CODE HERE
    # Try to fetch articles with retry
    # Show attempt number each time
    # Display success or failure message
    pass

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
