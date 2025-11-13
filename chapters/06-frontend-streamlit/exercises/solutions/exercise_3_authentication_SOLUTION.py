"""
Exercise 3: Authentication Flow 🟡 - SOLUTION
Difficulty: Intermediate
Estimated Time: 60 minutes

This is the complete solution with all TODOs implemented.

DEMO CREDENTIALS:
Email: john@example.com
Password: Password123!
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

# TODO 1: SOLUTION
def init_session_state():
    """Initialize session state variables for authentication."""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None

# TODO 2: SOLUTION
def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return st.session_state.token is not None and st.session_state.user is not None

# TODO 3: SOLUTION
def save_auth_data(token: str, user: Dict):
    """Save authentication data to session state."""
    st.session_state.token = token
    st.session_state.user = user

# TODO 4: SOLUTION
def logout():
    """Clear authentication data."""
    st.session_state.token = None
    st.session_state.user = None

# ============================================================================
# API CLIENT WITH AUTHENTICATION
# ============================================================================

class AuthAPIClient:
    """API client with authentication support."""

    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token

    # TODO 5: SOLUTION
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including auth token if available."""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    # TODO 6: SOLUTION
    def login(self, email: str, password: str) -> Dict:
        """Login with email and password."""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={'email': email, 'password': password},
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    # TODO 7: SOLUTION
    def register(self, name: str, email: str, password: str) -> Dict:
        """Register a new user."""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={'username': name, 'email': email, 'password': password},
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    # TODO 8: SOLUTION
    def get_protected_data(self) -> Dict:
        """Fetch data that requires authentication."""
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers=self._get_headers(),
            timeout=5
        )
        response.raise_for_status()
        return response.json()

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

# TODO 9: SOLUTION
if is_authenticated():
    st.success(f"✅ Welcome back, **{st.session_state.user['name']}**!")
    st.caption(f"📧 {st.session_state.user['email']}")
else:
    st.info("Please login or register to continue")

st.divider()

# ============================================================================
# SIDEBAR - USER INFO
# ============================================================================

with st.sidebar:
    st.subheader("👤 User Info")

    # TODO 10: SOLUTION
    if is_authenticated():
        st.write(f"**{st.session_state.user['name']}**")
        st.caption(st.session_state.user['email'])

        if st.button("🚪 Logout", type="primary"):
            logout()
            st.success("✅ Logged out!")
            st.rerun()
    else:
        st.info("👤 Not logged in")

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

        # TODO 11: SOLUTION
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("🔓 Login", type="primary")

            if submit:
                # Validation
                errors = []

                if not email:
                    errors.append("❌ Email is required")
                elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                    errors.append("❌ Invalid email format")

                if not password:
                    errors.append("❌ Password is required")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Attempt login
                    try:
                        api = AuthAPIClient(API_BASE_URL)
                        with st.spinner("Logging in..."):
                            response = api.login(email, password)

                        # Save auth data
                        save_auth_data(response['token'], response['user'])

                        st.success(f"✅ Welcome back, {response['user']['name']}!")
                        st.balloons()
                        st.rerun()

                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 401:
                            st.error("❌ Invalid email or password")
                        else:
                            st.error(f"❌ Login failed: {e}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

        # Demo credentials
        st.divider()
        with st.expander("🔑 Demo Credentials"):
            st.code("""
Email: john@example.com
Password: Password123!
            """)

    # ------------------------------------------------------------------------
    # REGISTER TAB
    # ------------------------------------------------------------------------

    with tab2:
        st.subheader("Create New Account")

        # TODO 12: SOLUTION
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="your.email@example.com")

            col1, col2 = st.columns(2)
            with col1:
                password = st.text_input("Password", type="password")
            with col2:
                confirm_password = st.text_input("Confirm Password", type="password")

            submit = st.form_submit_button("📝 Register", type="primary")

            if submit:
                # Validation
                errors = []

                if not name or len(name.strip()) < 2:
                    errors.append("❌ Name must be at least 2 characters")

                if not email:
                    errors.append("❌ Email is required")
                elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                    errors.append("❌ Invalid email format")

                if not password:
                    errors.append("❌ Password is required")
                elif len(password) < 6:
                    errors.append("❌ Password must be at least 6 characters")

                if password != confirm_password:
                    errors.append("❌ Passwords do not match")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Attempt registration
                    try:
                        api = AuthAPIClient(API_BASE_URL)
                        with st.spinner("Creating account..."):
                            response = api.register(name.strip(), email, password)

                        # Save auth data
                        save_auth_data(response['token'], response['user'])

                        st.success(f"✅ Account created! Welcome, {response['user']['name']}!")
                        st.balloons()
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Registration failed: {e}")

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

    # TODO 13: SOLUTION
    tab1, tab2, tab3 = st.tabs(["My Info", "Create Article", "My Activity"])

    with tab1:
        # TODO 14: SOLUTION
        st.subheader("📋 Your Information")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("User ID", st.session_state.user['id'])
            st.metric("Name", st.session_state.user['name'])

        with col2:
            st.metric("Email", st.session_state.user['email'])

        st.divider()
        st.subheader("🔑 Access Token")
        st.code(st.session_state.token[:50] + "...", language="text")
        st.caption("Token is used for authenticated API requests")

    with tab2:
        # TODO 15: SOLUTION
        st.subheader("✍️ Create Article")
        st.info("This demonstrates a protected endpoint that requires authentication.")

        with st.form("create_article_form"):
            title = st.text_input("Title")
            content = st.text_area("Content", height=200)
            submit = st.form_submit_button("Create", type="primary")

            if submit:
                if title and content:
                    st.success("✅ Article would be created with authentication token!")
                    st.code(f"Authorization: Bearer {st.session_state.token[:20]}...", language="text")
                else:
                    st.error("Please fill all fields")

    with tab3:
        # TODO 16: SOLUTION
        st.subheader("📊 Your Activity")

        st.markdown("""
        **This would display:**
        - Your articles
        - Your comments
        - Your activity history

        All fetched using authenticated API calls with your JWT token.
        """)

        if st.button("Fetch My Data"):
            try:
                api = AuthAPIClient(API_BASE_URL, st.session_state.token)
                with st.spinner("Loading..."):
                    data = api.get_protected_data()

                st.success("✅ Data fetched successfully!")
                st.json(data)

            except Exception as e:
                st.error(f"❌ Error: {e}")

# ============================================================================
# AUTHENTICATION FLOW DIAGRAM
# ============================================================================

st.divider()
st.header("📊 Authentication Flow")

# TODO 17: SOLUTION
st.markdown("""
### How JWT Authentication Works:

1. **User Login** → User submits email and password
2. **Backend Validation** → Backend validates credentials
3. **Token Generation** → Backend creates JWT token
4. **Token Storage** → Frontend stores token in session state
5. **Authenticated Requests** → Frontend includes token in API requests
6. **Token Validation** → Backend validates token for protected endpoints

### Example Authorization Header:
""")

st.code("""
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
""", language="text")

# ============================================================================
# TESTING SECTION
# ============================================================================

st.divider()
st.header("🧪 Testing")

with st.expander("Test Authentication States"):
    st.markdown("""
    ### Current Session State
    """)

    # TODO 18: SOLUTION
    st.json({
        "is_authenticated": is_authenticated(),
        "has_token": st.session_state.token is not None,
        "has_user": st.session_state.user is not None,
        "user_data": st.session_state.user if st.session_state.user else "Not logged in"
    })

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
