"""
Authentication utilities for managing user sessions
"""

import streamlit as st


def init_session_state():
    """Initialize authentication session state variables"""
    if 'token' not in st.session_state:
        st.session_state.token = None

    if 'user' not in st.session_state:
        st.session_state.user = None


def is_authenticated():
    """Check if user is currently authenticated"""
    return st.session_state.get('token') is not None


def get_current_user():
    """Get current authenticated user"""
    return st.session_state.get('user')


def get_token():
    """Get current authentication token"""
    return st.session_state.get('token')


def save_auth_data(token, user):
    """Save authentication data to session state"""
    st.session_state.token = token
    st.session_state.user = user


def clear_auth_data():
    """Clear authentication data (logout)"""
    st.session_state.token = None
    st.session_state.user = None


def require_auth():
    """Require authentication to access page - redirects if not authenticated"""
    if not is_authenticated():
        st.warning("⚠️ You must be logged in to access this page")
        st.info("👉 Please use the **Login** page from the sidebar")
        st.stop()


def show_user_info():
    """Display current user info in sidebar"""
    if is_authenticated():
        user = get_current_user()
        with st.sidebar:
            st.success(f"✅ Logged in as **{user['username']}**")
            st.caption(f"Email: {user['email']}")
    else:
        with st.sidebar:
            st.info("👤 Not logged in")
