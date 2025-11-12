"""
API Client for communicating with Flask backend
"""

import requests
from typing import Optional, Dict, Any
import streamlit as st


class BlogAPIClient:
    """Client for Blog API"""

    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with optional authentication"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise errors if needed"""
        if response.status_code >= 400:
            response.raise_for_status()
        return response.json()

    # ========== Authentication ==========

    def register(self, username: str, email: str, password: str, bio: str = None) -> Dict:
        """Register new user"""
        response = requests.post(
            f'{self.base_url}/auth/register',
            json={
                'username': username,
                'email': email,
                'password': password,
                'bio': bio
            }
        )
        return self._handle_response(response)

    def login(self, email: str, password: str) -> Dict:
        """Login and get JWT token"""
        response = requests.post(
            f'{self.base_url}/auth/login',
            json={'email': email, 'password': password}
        )
        return self._handle_response(response)

    def get_current_user(self) -> Dict:
        """Get current authenticated user"""
        response = requests.get(
            f'{self.base_url}/auth/me',
            headers=self._get_headers()
        )
        return self._handle_response(response)

    def logout(self) -> Dict:
        """Logout (blacklist token)"""
        response = requests.post(
            f'{self.base_url}/auth/logout',
            headers=self._get_headers()
        )
        return self._handle_response(response)

    # ========== Articles ==========

    def get_articles(self, params: Optional[Dict] = None) -> Dict:
        """Get articles with optional filters"""
        response = requests.get(
            f'{self.base_url}/articles',
            params=params
        )
        return self._handle_response(response)

    def get_article(self, article_id: int) -> Dict:
        """Get single article by ID"""
        response = requests.get(
            f'{self.base_url}/articles/{article_id}'
        )
        return self._handle_response(response)

    def create_article(self, data: Dict) -> Dict:
        """Create new article (requires authentication)"""
        response = requests.post(
            f'{self.base_url}/articles',
            json=data,
            headers=self._get_headers()
        )
        return self._handle_response(response)

    def update_article(self, article_id: int, data: Dict) -> Dict:
        """Update article (requires authentication and ownership)"""
        response = requests.put(
            f'{self.base_url}/articles/{article_id}',
            json=data,
            headers=self._get_headers()
        )
        return self._handle_response(response)

    def delete_article(self, article_id: int) -> None:
        """Delete article (requires authentication and ownership)"""
        response = requests.delete(
            f'{self.base_url}/articles/{article_id}',
            headers=self._get_headers()
        )
        if response.status_code != 204:
            response.raise_for_status()

    def upload_article_image(self, article_id: int, file) -> Dict:
        """Upload image for article"""
        files = {'file': file}
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        response = requests.post(
            f'{self.base_url}/articles/{article_id}/image',
            files=files,
            headers=headers
        )
        return self._handle_response(response)

    # ========== Comments ==========

    def get_article_comments(self, article_id: int) -> Dict:
        """Get comments for an article"""
        response = requests.get(
            f'{self.base_url}/articles/{article_id}/comments'
        )
        return self._handle_response(response)

    def create_comment(self, article_id: int, data: Dict) -> Dict:
        """Add comment to article"""
        response = requests.post(
            f'{self.base_url}/articles/{article_id}/comments',
            json=data
        )
        return self._handle_response(response)

    # ========== Authors ==========

    def get_authors(self) -> Dict:
        """Get all authors"""
        response = requests.get(
            f'{self.base_url}/authors'
        )
        return self._handle_response(response)

    def get_author(self, author_id: int) -> Dict:
        """Get author by ID"""
        response = requests.get(
            f'{self.base_url}/authors/{author_id}'
        )
        return self._handle_response(response)

    def get_author_articles(self, author_id: int) -> Dict:
        """Get articles by specific author"""
        response = requests.get(
            f'{self.base_url}/authors/{author_id}/articles'
        )
        return self._handle_response(response)


def handle_api_error(error: Exception):
    """Handle API errors with user-friendly messages"""
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("❌ Cannot connect to backend API")
        st.info("Make sure the Flask backend is running:")
        st.code("cd backend && python app.py", language="bash")

    elif isinstance(error, requests.exceptions.Timeout):
        st.error("⏱️ Request timeout - Backend is taking too long to respond")

    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = error.response.status_code

        if status_code == 400:
            # Validation errors
            try:
                errors = error.response.json().get('errors', {})
                st.error("❌ Validation errors:")
                for field, messages in errors.items():
                    for msg in messages:
                        st.error(f"  • **{field}**: {msg}")
            except:
                st.error(f"❌ Bad request: {error.response.text}")

        elif status_code == 401:
            st.error("🔒 Session expired or invalid credentials")
            st.info("Please login again")
            # Clear token
            if 'token' in st.session_state:
                st.session_state.token = None

        elif status_code == 403:
            st.error("⛔ Access denied")
            st.info("You don't have permission to perform this action")

        elif status_code == 404:
            st.error("🔍 Resource not found")

        elif status_code >= 500:
            st.error("🔥 Server error")
            st.info("Something went wrong on the backend. Please try again later.")

        else:
            st.error(f"❌ Error: {status_code}")

    else:
        st.error(f"❌ Unexpected error: {str(error)}")
        with st.expander("Error details"):
            st.exception(error)
