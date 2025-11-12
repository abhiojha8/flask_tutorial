"""
Exercise 3: Authentication Flow 🟡
Difficulty: Intermediate
Estimated Time: 60 minutes

GOAL:
Implement a complete authentication system with login, registration,
and session management using JWT tokens.

LEARNING OBJECTIVES:
- Understand JWT authentication flow
- Manage session state for auth
- Implement login and registration forms
- Handle protected routes
- Store and use authentication tokens

REQUIREMENTS:
1. Create login form with validation
2. Create registration form with validation
3. Store JWT token in session state
4. Show user info when logged in
5. Implement logout functionality
6. Create a protected page example

INSTRUCTIONS:
1. Look for TODO comments
2. Implement the required functionality
3. Run: streamlit run exercise_3_authentication.py
4. Test login, registration, and logout

DEMO CREDENTIALS:
Email: john.doe@example.com
Password: password123
"""

import streamlit as st
import requests
import re
from typing import Optional, Dict

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# TODO 1: Initialize session state for authentication
# Create function init_session_state() that:
# - Checks if 'token' exists in session_state, if not set to None
# - Checks if 'user' exists in session_state, if not set to None
#
# Hint: if 'key' not in st.session_state:
#           st.session_state.key = value

def init_session_state():
    """Initialize session state variables for authentication."""
    # YOUR CODE HERE
    pass

# TODO 2: Create is_authenticated() helper function
# This should return True if user is logged in, False otherwise
# Hint: Check if both token and user exist in session_state

def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    # YOUR CODE HERE
    pass

# TODO 3: Create save_auth_data() helper function
# This should:
# - Accept token and user parameters
# - Save them to session_state
# Hint: st.session_state.token = token

def save_auth_data(token: str, user: Dict):
    """Save authentication data to session state."""
    # YOUR CODE HERE
    pass

# TODO 4: Create logout() helper function
# This should:
# - Clear token from session_state
# - Clear user from session_state
# Hint: st.session_state.token = None

def logout():
    """Clear authentication data."""
    # YOUR CODE HERE
    pass

# ============================================================================
# API CLIENT WITH AUTHENTICATION
# ============================================================================

class AuthAPIClient:
    """API client with authentication support."""

    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token

    # TODO 5: Create _get_headers() method
    # This should:
    # - Return headers dictionary
    # - Include 'Content-Type': 'application/json'
    # - If token exists, include 'Authorization': f'Bearer {self.token}'
    #
    # Hint: Create a dict with headers
    # Hint: Check if self.token before adding Authorization

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including auth token if available."""
        # YOUR CODE HERE
        pass

    # TODO 6: Implement login() method
    # This should:
    # - Accept email and password
    # - Make POST request to /auth/login
    # - Send JSON body with email and password
    # - Return the JSON response
    #
    # Hint: requests.post(url, json={'email': email, 'password': password})
    # Hint: response.raise_for_status()

    def login(self, email: str, password: str) -> Dict:
        """
        Login with email and password.

        Returns:
            Dict with access_token and user info
        """
        # YOUR CODE HERE
        pass

    # TODO 7: Implement register() method
    # This should:
    # - Accept name, email, password
    # - Make POST request to /auth/register
    # - Send JSON body with name, email, password
    # - Return the JSON response
    #
    # Hint: Similar to login but different endpoint

    def register(self, name: str, email: str, password: str) -> Dict:
        """
        Register a new user.

        Returns:
            Dict with access_token and user info
        """
        # YOUR CODE HERE
        pass

    # TODO 8: Implement get_protected_data() method
    # This should:
    # - Make GET request to /protected-endpoint
    # - Include authentication headers
    # - Return the response
    #
    # Hint: Use headers=self._get_headers()

    def get_protected_data(self) -> Dict:
        """
        Fetch data that requires authentication.
        This is a placeholder - backend may not have this endpoint.
        """
        # YOUR CODE HERE
        pass

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Exercise 3 | Authentication",
    page_icon="🔐",
    layout="wide"
)

# Initialize session state
init_session_state()

# ============================================================================
# HEADER
# ============================================================================

st.title("🔐 Authentication System")

# TODO 9: Show different header based on authentication status
# If authenticated:
# - Show welcome message with user name
# - Show user email
# If not authenticated:
# - Show message to login or register
#
# Hint: Use is_authenticated()
# Hint: Access user data with st.session_state.user

# YOUR CODE HERE


st.divider()

# ============================================================================
# SIDEBAR - USER INFO
# ============================================================================

with st.sidebar:
    st.subheader("👤 User Info")

    # TODO 10: Show user info in sidebar
    # If authenticated:
    # - Show user name
    # - Show user email
    # - Show logout button
    # If not authenticated:
    # - Show "Not logged in" message
    #
    # Hint: Use is_authenticated()
    # Hint: On logout button click, call logout() and st.rerun()

    # YOUR CODE HERE
    pass

# ============================================================================
# MAIN CONTENT - LOGIN/REGISTER OR PROTECTED CONTENT
# ============================================================================

if not is_authenticated():
    # ========================================================================
    # LOGIN/REGISTER TABS
    # ========================================================================

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ------------------------------------------------------------------------
    # LOGIN TAB
    # ------------------------------------------------------------------------

    with tab1:
        st.subheader("Login to Your Account")

        # TODO 11: Create login form
        # Form should have:
        # - Email input
        # - Password input
        # - Submit button
        # On submit:
        # - Validate inputs (not empty, email format)
        # - Try to login using API
        # - Save auth data on success
        # - Show error on failure
        # - Rerun to show logged-in state
        #
        # Hint: Use st.form("login_form")
        # Hint: Validate email with regex: r'^[\w\.-]+@[\w\.-]+\.\w+$'
        # Hint: Use try/except for API call

        # YOUR CODE HERE
        pass

    # ------------------------------------------------------------------------
    # REGISTER TAB
    # ------------------------------------------------------------------------

    with tab2:
        st.subheader("Create New Account")

        # TODO 12: Create registration form
        # Form should have:
        # - Name input
        # - Email input
        # - Password input
        # - Confirm password input
        # - Submit button
        # On submit:
        # - Validate all inputs
        # - Check passwords match
        # - Check password length >= 6
        # - Try to register using API
        # - Save auth data on success
        # - Show error on failure
        # - Rerun to show logged-in state
        #
        # Hint: Similar to login form
        # Hint: Check password == confirm_password

        # YOUR CODE HERE
        pass

else:
    # ========================================================================
    # PROTECTED CONTENT (User is logged in)
    # ========================================================================

    st.success("✅ You are authenticated!")

    st.divider()
    st.header("🎯 Protected Features")

    st.markdown("""
    This section is only visible to authenticated users.
    You can now:
    - Create articles
    - Post comments
    - Edit your content
    - View your profile
    """)

    # TODO 13: Create tabs for different protected features
    # Create 3 tabs: "My Info", "Create Article", "My Activity"
    #
    # Hint: Use st.tabs()

    # YOUR CODE HERE
    tab1, tab2, tab3 = st.tabs(["My Info", "Create Article", "My Activity"])

    with tab1:
        # TODO 14: Display user information
        # Show:
        # - User ID
        # - Name
        # - Email
        # - Token (first 20 chars only for security)
        #
        # Hint: Use st.session_state.user
        # Hint: Use st.code() to display token

        st.subheader("📋 Your Information")
        # YOUR CODE HERE
        pass

    with tab2:
        # TODO 15: Create a simple article creation form
        # This is a placeholder - doesn't need to actually work
        # Form should have:
        # - Title input
        # - Content textarea
        # - Submit button
        # On submit:
        # - Show success message
        # - Show that auth token would be used
        #
        # Hint: st.form()
        # Hint: Mention this demonstrates protected endpoint

        st.subheader("✍️ Create Article")
        st.info("This demonstrates a protected endpoint that requires authentication.")

        # YOUR CODE HERE
        pass

    with tab3:
        # TODO 16: Display activity/stats
        # Show:
        # - Message that this would show user's articles
        # - Message that this would show user's comments
        # - Example of authenticated API call
        #
        # Hint: Just display placeholder content

        st.subheader("📊 Your Activity")
        # YOUR CODE HERE
        pass

# ============================================================================
# AUTHENTICATION FLOW DIAGRAM
# ============================================================================

st.divider()
st.header("📊 Authentication Flow")

# TODO 17: Display authentication flow explanation
# Show a diagram or explanation of:
# 1. User submits credentials
# 2. Backend validates and returns JWT
# 3. Frontend stores JWT in session state
# 4. Frontend includes JWT in subsequent requests
# 5. Backend validates JWT for protected endpoints
#
# Hint: Use st.markdown() with bullet points
# Hint: Use st.code() to show example Authorization header

# YOUR CODE HERE


# ============================================================================
# TESTING SECTION
# ============================================================================

st.divider()
st.header("🧪 Testing")

with st.expander("Test Authentication States"):
    st.markdown("""
    ### Current Session State

    This shows the current authentication state:
    """)

    # TODO 18: Display current session state
    # Show:
    # - Is authenticated?
    # - Token exists?
    # - User data exists?
    #
    # Hint: Use st.json() to display session state

    # YOUR CODE HERE
    pass

# ============================================================================
# COMPLETION CHECK
# ============================================================================

st.divider()

st.success("""
✅ **Exercise 3 Complete!**

You've learned how to:
- Implement login and registration forms
- Manage JWT tokens
- Use session state for authentication
- Create protected routes
- Handle authentication state
- Build a complete auth flow

**Next Step:** Move on to Exercise 4 to build CRUD operations!
""")

# ============================================================================
# HINTS AND TIPS
# ============================================================================

with st.expander("💡 Hints and Tips"):
    st.markdown("""
    ### JWT Token Structure

    A JWT token has 3 parts separated by dots:
    ```
    header.payload.signature
    ```

    ### Session State Best Practices

    1. **Initialize at the top:** Always init session state before using
    2. **Use helper functions:** Create is_authenticated(), logout(), etc.
    3. **Clear on logout:** Set to None, not just delete

    ### Security Considerations

    1. **Never log tokens:** Don't print tokens to console
    2. **HTTPS in production:** Always use HTTPS in production
    3. **Token expiration:** Tokens should expire
    4. **Secure storage:** Consider encrypted storage for sensitive apps

    ### Common Issues

    **Token not being sent:**
    - Check headers include Authorization
    - Format: 'Bearer <token>'

    **Session state not persisting:**
    - Make sure you call init_session_state()
    - Don't overwrite session_state accidentally

    **401 Errors:**
    - Token may have expired
    - Token format may be wrong
    - Backend may not be configured correctly
    """)
