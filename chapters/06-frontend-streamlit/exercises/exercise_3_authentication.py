"""
Exercise 3: Authentication Flow 🟡
Difficulty: Intermediate
Estimated Time: 60 minutes

SOLUTION
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

# SOLUTION 1: Initialize session state
def init_session_state():
    """Initialize session state variables for authentication."""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None

# SOLUTION 2: is_authenticated helper
def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return (st.session_state.token is not None and
            st.session_state.user is not None)

# SOLUTION 3: save_auth_data helper
def save_auth_data(token: str, user: Dict):
    """Save authentication data to session state."""
    st.session_state.token = token
    st.session_state.user = user

# SOLUTION 4: logout helper
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

    # SOLUTION 5: _get_headers method
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers including auth token if available."""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    # SOLUTION 6: login method
    def login(self, email: str, password: str) -> Dict:
        """Login with email and password."""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={'email': email, 'password': password},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 7: register method
    def register(self, name: str, email: str, password: str) -> Dict:
        """Register a new user."""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={'name': name, 'email': email, 'password': password},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 8: get_protected_data method
    def get_protected_data(self) -> Dict:
        """Fetch data that requires authentication."""
        response = requests.get(
            f"{self.base_url}/articles",  # Using articles as example
            headers=self._get_headers(),
            timeout=10
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

# SOLUTION 9: Show different header based on auth status
if is_authenticated():
    st.success(f"✅ Welcome back, **{st.session_state.user['name']}**!")
    st.caption(f"Logged in as: {st.session_state.user['email']}")
else:
    st.info("👋 Please login or register to continue")

st.divider()

# ============================================================================
# SIDEBAR - USER INFO
# ============================================================================

with st.sidebar:
    st.subheader("👤 User Info")

    # SOLUTION 10: Show user info in sidebar
    if is_authenticated():
        st.success("🟢 Logged In")
        st.write(f"**Name:** {st.session_state.user['name']}")
        st.write(f"**Email:** {st.session_state.user['email']}")

        st.divider()

        if st.button("🚪 Logout", type="primary"):
            logout()
            st.success("✅ Logged out successfully!")
            st.rerun()
    else:
        st.warning("🔴 Not Logged In")
        st.caption("Please login to access protected features")

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

        # SOLUTION 11: Login form
        with st.form("login_form"):
            login_email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            login_submit = st.form_submit_button("🔓 Login", type="primary")

            if login_submit:
                # Validation
                errors = []

                if not login_email:
                    errors.append("❌ Email is required")
                elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', login_email):
                    errors.append("❌ Invalid email format")

                if not login_password:
                    errors.append("❌ Password is required")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Attempt login
                    try:
                        api = AuthAPIClient(API_BASE_URL)

                        with st.spinner("Logging in..."):
                            response = api.login(login_email, login_password)

                        # Save auth data
                        save_auth_data(response['access_token'], response['user'])

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
        with st.expander("🔑 Demo Credentials"):
            st.code("Email: john.doe@example.com\nPassword: password123")

    # ------------------------------------------------------------------------
    # REGISTER TAB
    # ------------------------------------------------------------------------

    with tab2:
        st.subheader("Create New Account")

        # SOLUTION 12: Registration form
        with st.form("register_form"):
            register_name = st.text_input(
                "Full Name",
                placeholder="John Doe"
            )

            register_email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com"
            )

            col1, col2 = st.columns(2)

            with col1:
                register_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="At least 6 characters"
                )

            with col2:
                register_password_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter password"
                )

            register_submit = st.form_submit_button("📝 Register", type="primary")

            if register_submit:
                # Validation
                errors = []

                if not register_name or len(register_name.strip()) < 2:
                    errors.append("❌ Name must be at least 2 characters")

                if not register_email:
                    errors.append("❌ Email is required")
                elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', register_email):
                    errors.append("❌ Invalid email format")

                if not register_password:
                    errors.append("❌ Password is required")
                elif len(register_password) < 6:
                    errors.append("❌ Password must be at least 6 characters")

                if register_password != register_password_confirm:
                    errors.append("❌ Passwords do not match")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Attempt registration
                    try:
                        api = AuthAPIClient(API_BASE_URL)

                        with st.spinner("Creating account..."):
                            response = api.register(
                                register_name.strip(),
                                register_email,
                                register_password
                            )

                        # Save auth data
                        save_auth_data(response['access_token'], response['user'])

                        st.success(f"✅ Account created! Welcome, {response['user']['name']}!")
                        st.balloons()
                        st.rerun()

                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 400:
                            st.error("❌ Email already registered")
                        else:
                            st.error(f"❌ Registration failed: {e}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

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

    # SOLUTION 13: Create tabs for protected features
    tab1, tab2, tab3 = st.tabs(["My Info", "Create Article", "My Activity"])

    with tab1:
        # SOLUTION 14: Display user information
        st.subheader("📋 Your Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**User ID:**")
            st.code(st.session_state.user['id'])

            st.write("**Name:**")
            st.code(st.session_state.user['name'])

        with col2:
            st.write("**Email:**")
            st.code(st.session_state.user['email'])

            st.write("**Token (first 20 chars):**")
            st.code(st.session_state.token[:20] + "...")

    with tab2:
        # SOLUTION 15: Article creation form placeholder
        st.subheader("✍️ Create Article")
        st.info("This demonstrates a protected endpoint that requires authentication.")

        with st.form("create_article"):
            title = st.text_input("Title", placeholder="My Article")
            content = st.text_area("Content", placeholder="Write your article...")
            submit = st.form_submit_button("Create")

            if submit:
                if title and content:
                    st.success(f"✅ Article '{title}' would be created!")
                    st.info(f"Auth token would be sent: Bearer {st.session_state.token[:20]}...")
                else:
                    st.error("❌ Both title and content are required")

    with tab3:
        # SOLUTION 16: Activity/stats display
        st.subheader("📊 Your Activity")

        st.info("This would show your articles and comments")

        # Example of authenticated API call
        if st.button("Fetch My Data"):
            try:
                api = AuthAPIClient(API_BASE_URL, st.session_state.token)
                with st.spinner("Loading..."):
                    data = api.get_protected_data()

                st.success("✅ Data fetched with authentication!")
                st.write(f"Fetched {len(data['articles'])} articles")

            except Exception as e:
                st.error(f"❌ Error: {e}")

# ============================================================================
# AUTHENTICATION FLOW DIAGRAM
# ============================================================================

st.divider()
st.header("📊 Authentication Flow")

# SOLUTION 17: Display authentication flow
st.markdown("""
### How JWT Authentication Works

1. **User Login/Register**
   - User submits credentials
   - Backend validates credentials

2. **JWT Token Issued**
   - Backend generates JWT token
   - Token contains user info (encrypted)
   - Token is returned to frontend

3. **Token Storage**
   - Frontend stores token in session state
   - Token persists across page reruns

4. **Protected Requests**
   - Frontend includes token in requests
   - Header format: `Authorization: Bearer <token>`

5. **Token Validation**
   - Backend validates token
   - Checks if token is valid and not expired
   - Returns protected data if valid

### Example Authorization Header
""")

st.code(f"Authorization: Bearer {st.session_state.token[:40] if st.session_state.token else 'YOUR_JWT_TOKEN_HERE'}...", language="text")

# ============================================================================
# TESTING SECTION
# ============================================================================

st.divider()
st.header("🧪 Testing")

with st.expander("Test Authentication States"):
    st.markdown("""
    ### Current Session State
    """)

    # SOLUTION 18: Display session state
    st.write("**Is Authenticated:**", is_authenticated())
    st.write("**Token Exists:**", st.session_state.token is not None)
    st.write("**User Data Exists:**", st.session_state.user is not None)

    st.divider()

    st.write("**Current Session State:**")
    st.json({
        'token': st.session_state.token[:40] + "..." if st.session_state.token else None,
        'user': st.session_state.user
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
