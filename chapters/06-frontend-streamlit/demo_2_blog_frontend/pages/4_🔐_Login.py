"""
Login and Registration Page
Handles user authentication
"""

import streamlit as st
import sys
from pathlib import Path
import re

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from config import API_BASE_URL
from utils.auth import init_session_state, is_authenticated, save_auth_data, logout
from utils.api_client import BlogAPIClient, handle_api_error

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Login | Blog App",
    page_icon="🔐",
    layout="wide"
)

# Initialize session state
init_session_state()

# ============================================================================
# ALREADY LOGGED IN CHECK
# ============================================================================

if is_authenticated():
    st.success(f"✅ You are already logged in as **{st.session_state.user['name']}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏠 Go to Home"):
            st.switch_page("app.py")

    with col2:
        if st.button("✍️ Create Article"):
            st.switch_page("pages/2_✍️_Create_Article.py")

    with col3:
        if st.button("👤 View My Profile"):
            st.session_state.selected_author_id = st.session_state.user['id']
            st.switch_page("pages/3_👤_Authors.py")

    st.divider()

    # Logout section
    st.subheader("Logout")

    if st.button("🚪 Logout", type="primary"):
        logout()
        st.success("✅ Logged out successfully!")
        st.rerun()

    st.stop()

# ============================================================================
# LOGIN/REGISTER TABS
# ============================================================================

st.title("🔐 Authentication")

tab1, tab2 = st.tabs(["Login", "Register"])

# ============================================================================
# LOGIN TAB
# ============================================================================

with tab1:
    st.subheader("Login to Your Account")

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
                    api = BlogAPIClient(API_BASE_URL)

                    with st.spinner("Logging in..."):
                        response = api.login(login_email, login_password)

                    # Save auth data
                    save_auth_data(response['access_token'], response['user'])

                    st.success(f"✅ Welcome back, {response['user']['name']}!")
                    st.balloons()

                    # Redirect
                    import time
                    time.sleep(2)
                    st.rerun()

                except Exception as e:
                    handle_api_error(e)

    # Demo credentials
    st.divider()

    with st.expander("🔑 Demo Credentials", expanded=False):
        st.markdown("""
        Try logging in with these demo accounts:

        **User 1:**
        - Email: `john.doe@example.com`
        - Password: `password123`

        **User 2:**
        - Email: `jane.smith@example.com`
        - Password: `password123`

        **User 3:**
        - Email: `bob.johnson@example.com`
        - Password: `password123`
        """)

# ============================================================================
# REGISTER TAB
# ============================================================================

with tab2:
    st.subheader("Create New Account")

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
                    api = BlogAPIClient(API_BASE_URL)

                    with st.spinner("Creating account..."):
                        response = api.register(
                            register_name.strip(),
                            register_email,
                            register_password
                        )

                    # Save auth data
                    save_auth_data(response['access_token'], response['user'])

                    st.success(f"✅ Account created successfully! Welcome, {response['user']['name']}!")
                    st.balloons()

                    # Redirect
                    import time
                    time.sleep(2)
                    st.rerun()

                except Exception as e:
                    handle_api_error(e)

    # Registration tips
    st.divider()

    with st.expander("💡 Registration Tips", expanded=False):
        st.markdown("""
        ### Password Requirements

        - **Minimum length:** 6 characters
        - **Recommended:** Use a mix of letters, numbers, and symbols
        - **Avoid:** Common passwords like "password123"

        ### Email

        - Must be a valid email address
        - Used for login and notifications
        - One account per email address

        ### Name

        - Will be displayed on your articles and comments
        - Can be your real name or a pen name
        - At least 2 characters
        """)

# ============================================================================
# INFORMATION SECTION
# ============================================================================

st.divider()

st.header("ℹ️ About Authentication")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔐 Why Login?

    Create an account to:
    - ✍️ Write and publish articles
    - 💬 Comment on articles
    - ✏️ Edit your own content
    - 👤 Build your author profile
    """)

with col2:
    st.markdown("""
    ### 🛡️ Security

    We keep your account safe with:
    - 🔒 Encrypted password storage
    - 🎫 JWT token authentication
    - 🚫 Secure session management
    - ✅ Input validation
    """)

st.divider()

st.markdown("""
### 🎯 Quick Start Guide

1. **Register** a new account or **Login** with existing credentials
2. Browse articles on the **Home** page
3. Create your first article using the **Create Article** page
4. Engage with the community by leaving comments
5. View author profiles on the **Authors** page
""")

# ============================================================================
# NAVIGATION
# ============================================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")

with col2:
    if st.button("📝 View Articles"):
        st.switch_page("pages/1_📝_Articles.py")
