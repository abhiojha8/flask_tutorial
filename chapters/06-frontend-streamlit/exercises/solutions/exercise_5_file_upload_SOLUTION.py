"""
Exercise 5: File Upload & Validation 🔴 - SOLUTION
Difficulty: Advanced
Estimated Time: 90 minutes

Complete solution with all TODOs implemented.

DEMO CREDENTIALS:
Email: john@example.com
Password: Password123!

NOTE: Requires Pillow library for image processing
"""

import streamlit as st
import requests
from typing import Optional, Dict
from io import BytesIO

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    st.error("❌ PIL (Pillow) not installed. Run: pip install Pillow")

API_BASE_URL = 'http://localhost:5000/api'

# Configuration
MAX_FILE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_session_state():
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'selected_article_id' not in st.session_state:
        st.session_state.selected_article_id = None

def is_authenticated() -> bool:
    return st.session_state.token is not None

def require_auth():
    if not is_authenticated():
        st.warning("⚠️ Please login first")
        with st.form("quick_login"):
            email = st.text_input("Email", value="john@example.com")
            password = st.text_input("Password", type="password", value="Password123!")
            if st.form_submit_button("Login"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={'email': email, 'password': password}
                    )
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.token = data['token']
                    st.session_state.user = data['user']
                    st.success("✅ Logged in!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Login failed: {e}")
        st.stop()

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

# TODO 1: SOLUTION
def validate_file_size(uploaded_file) -> tuple[bool, Optional[str]]:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.2f}MB) exceeds maximum ({MAX_FILE_SIZE_MB}MB)"
    return True, None

# TODO 2: SOLUTION
def validate_file_type(uploaded_file) -> tuple[bool, Optional[str]]:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in ALLOWED_IMAGE_TYPES:
        return False, f"File type '.{file_extension}' not allowed. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
    return True, None

# TODO 3: SOLUTION
def validate_image_content(uploaded_file) -> tuple[bool, Optional[str]]:
    if not PIL_AVAILABLE:
        return False, "PIL not installed"

    try:
        img = Image.open(BytesIO(uploaded_file.read()))
        img.verify()
        uploaded_file.seek(0)  # Reset file pointer
        return True, None
    except Exception as e:
        uploaded_file.seek(0)
        return False, f"Invalid image file: {str(e)}"

# TODO 4: SOLUTION
def get_image_info(uploaded_file) -> Optional[Dict]:
    if not PIL_AVAILABLE:
        return None

    try:
        img = Image.open(BytesIO(uploaded_file.read()))
        info = {
            'width': img.size[0],
            'height': img.size[1],
            'format': img.format,
            'mode': img.mode
        }
        uploaded_file.seek(0)  # Reset file pointer
        return info
    except Exception:
        uploaded_file.seek(0)
        return None

# ============================================================================
# API CLIENT
# ============================================================================

class FileUploadAPIClient:
    def __init__(self, token: str):
        self.base_url = API_BASE_URL
        self.token = token

    def _get_headers(self, include_content_type: bool = True) -> Dict[str, str]:
        headers = {'Authorization': f'Bearer {self.token}'}
        if include_content_type:
            headers['Content-Type'] = 'application/json'
        return headers

    def get_articles(self) -> Dict:
        response = requests.get(
            f"{self.base_url}/articles",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_article(self, article_id: int) -> Dict:
        response = requests.get(
            f"{self.base_url}/articles/{article_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    # TODO 5: SOLUTION
    def upload_article_image(self, article_id: int, uploaded_file) -> Dict:
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        headers = self._get_headers(include_content_type=False)

        response = requests.post(
            f"{self.base_url}/articles/{article_id}/image",
            files=files,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Exercise 5 | File Upload",
    page_icon="🖼️",
    layout="wide"
)

init_session_state()
require_auth()

api = FileUploadAPIClient(st.session_state.token)

# ============================================================================
# HEADER
# ============================================================================

st.title("🖼️ Image Upload System")
st.caption(f"Welcome, {st.session_state.user['name']}!")

st.markdown(f"""
This exercise demonstrates file upload with validation and backend integration.

**Requirements:**
- Max file size: {MAX_FILE_SIZE_MB}MB
- Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}
""")

st.divider()

# ============================================================================
# ARTICLE SELECTION
# ============================================================================

st.header("1️⃣ Select Article")

# TODO 6: SOLUTION
try:
    response = api.get_articles()
    all_articles = response['articles']

    my_articles = [a for a in all_articles if a['author']['id'] == st.session_state.user['id']]

    if my_articles:
        article_options = {f"{a['title']} (ID: {a['id']})": a['id'] for a in my_articles}

        selected = st.selectbox(
            "Select an article to add an image to:",
            options=list(article_options.keys())
        )

        st.session_state.selected_article_id = article_options[selected]

        st.success(f"✅ Selected article ID: {st.session_state.selected_article_id}")

    else:
        st.info("You don't have any articles yet. Create one first!")
        st.stop()

except Exception as e:
    st.error(f"❌ Error loading articles: {e}")
    st.stop()

st.divider()

# ============================================================================
# FILE UPLOAD SECTION
# ============================================================================

st.header("2️⃣ Upload Image")

if st.session_state.selected_article_id:

    # TODO 7: SOLUTION
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'gif'],
        help=f"Max size: {MAX_FILE_SIZE_MB}MB. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
    )

    if uploaded_file is not None:

        # ====================================================================
        # VALIDATION
        # ====================================================================

        st.subheader("✅ Validation")

        # TODO 8: SOLUTION
        size_valid, size_error = validate_file_size(uploaded_file)
        if size_valid:
            st.success(f"✅ File size OK: {uploaded_file.size / (1024*1024):.2f}MB")
        else:
            st.error(f"❌ {size_error}")

        # TODO 9: SOLUTION
        type_valid, type_error = validate_file_type(uploaded_file)
        if type_valid:
            st.success(f"✅ File type OK: {uploaded_file.name.split('.')[-1]}")
        else:
            st.error(f"❌ {type_error}")

        # TODO 10: SOLUTION
        content_valid, content_error = validate_image_content(uploaded_file)
        if content_valid:
            st.success("✅ Valid image file")
        else:
            st.error(f"❌ {content_error}")

        # TODO 11: SOLUTION
        all_valid = size_valid and type_valid and content_valid

        if all_valid:

            # ================================================================
            # IMAGE PREVIEW
            # ================================================================

            st.subheader("👁️ Preview")

            # TODO 12: SOLUTION
            col1, col2 = st.columns([2, 1])

            with col1:
                st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

            with col2:
                image_info = get_image_info(uploaded_file)

                if image_info:
                    st.metric("Width", f"{image_info['width']}px")
                    st.metric("Height", f"{image_info['height']}px")
                    st.metric("Format", image_info['format'])
                    st.caption(f"Mode: {image_info['mode']}")

                file_size_kb = uploaded_file.size / 1024
                st.metric("Size", f"{file_size_kb:.2f} KB")

            # ================================================================
            # UPLOAD TO BACKEND
            # ================================================================

            st.subheader("📤 Upload")

            # TODO 13: SOLUTION
            if st.button("📤 Upload Image", type="primary"):
                try:
                    with st.spinner("Uploading..."):
                        result = api.upload_article_image(
                            st.session_state.selected_article_id,
                            uploaded_file
                        )

                    st.success("✅ Image uploaded successfully!")
                    st.info(f"Image URL: {result.get('image_url', 'N/A')}")

                    st.balloons()

                    # Show uploaded image
                    if result.get('image_url'):
                        st.image(
                            f"http://localhost:5000{result['image_url']}",
                            caption="Uploaded Image",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

        else:
            st.warning("⚠️ Please fix validation errors before uploading")

else:
    st.info("Please select an article first")

st.divider()

# ============================================================================
# CURRENT ARTICLE IMAGE
# ============================================================================

st.header("3️⃣ Current Article Image")

if st.session_state.selected_article_id:
    # TODO 14: SOLUTION
    try:
        with st.spinner("Loading article..."):
            article = api.get_article(st.session_state.selected_article_id)

        if article.get('image_url'):
            st.info(f"Current image: {article['image_url']}")
            st.image(
                f"http://localhost:5000{article['image_url']}",
                caption=f"Current image for: {article['title']}",
                use_container_width=True
            )
        else:
            st.info("📭 No image uploaded for this article yet")

    except Exception as e:
        st.error(f"❌ Error loading article: {e}")

st.divider()

# ============================================================================
# COMPLETION CHECK
# ============================================================================

st.success("""
✅ **Exercise 5 Complete!**

You've learned how to:
- Handle file uploads in Streamlit
- Validate file size and type
- Verify file content with PIL
- Preview images before upload
- Make multipart/form-data requests
- Integrate with backend upload endpoints
- Handle errors gracefully
- Follow security best practices

**Congratulations!** You've completed all Chapter 6 exercises!
""")
