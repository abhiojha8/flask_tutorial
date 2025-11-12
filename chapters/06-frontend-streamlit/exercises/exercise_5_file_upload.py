"""
Exercise 5: File Upload & Validation 🔴
Difficulty: Advanced
Estimated Time: 90 minutes

SOLUTION
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

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# Configuration
MAX_FILE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_session_state():
    """Initialize session state."""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'selected_article_id' not in st.session_state:
        st.session_state.selected_article_id = None

def is_authenticated() -> bool:
    """Check if user is logged in."""
    return st.session_state.token is not None

def require_auth():
    """Redirect to login if not authenticated."""
    if not is_authenticated():
        st.warning("⚠️ Please login first")
        with st.form("quick_login"):
            email = st.text_input("Email", value="john.doe@example.com")
            password = st.text_input("Password", type="password", value="password123")
            if st.form_submit_button("Login"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={'email': email, 'password': password}
                    )
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.token = data['access_token']
                    st.session_state.user = data['user']
                    st.success("✅ Logged in!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Login failed: {e}")
        st.stop()

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

# SOLUTION 1: validate_file_size
def validate_file_size(uploaded_file) -> tuple[bool, Optional[str]]:
    """Validate file size is within limits."""
    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.2f}MB) exceeds maximum ({MAX_FILE_SIZE_MB}MB)"

    return True, None

# SOLUTION 2: validate_file_type
def validate_file_type(uploaded_file) -> tuple[bool, Optional[str]]:
    """Validate file type is an allowed image format."""
    if not uploaded_file.name:
        return False, "File has no name"

    # Extract extension
    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension not in ALLOWED_IMAGE_TYPES:
        return False, f"File type '{file_extension}' not allowed. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"

    return True, None

# SOLUTION 3: validate_image_content
def validate_image_content(uploaded_file) -> tuple[bool, Optional[str]]:
    """Validate file is actually a valid image using PIL."""
    if not PIL_AVAILABLE:
        return False, "PIL not installed"

    try:
        # Read file content
        file_bytes = uploaded_file.read()

        # Try to open as image
        img = Image.open(BytesIO(file_bytes))

        # Verify it's a valid image
        img.verify()

        # Reset file pointer
        uploaded_file.seek(0)

        return True, None

    except Exception as e:
        # Reset file pointer
        uploaded_file.seek(0)
        return False, f"Invalid image file: {str(e)}"

# SOLUTION 4: get_image_info
def get_image_info(uploaded_file) -> Optional[Dict]:
    """Extract image information using PIL."""
    if not PIL_AVAILABLE:
        return None

    try:
        # Read file content
        file_bytes = uploaded_file.read()

        # Open image
        img = Image.open(BytesIO(file_bytes))

        # Get info
        info = {
            'width': img.size[0],
            'height': img.size[1],
            'format': img.format,
            'mode': img.mode,
            'size_mb': uploaded_file.size / (1024 * 1024)
        }

        # Reset file pointer
        uploaded_file.seek(0)

        return info

    except Exception:
        # Reset file pointer
        uploaded_file.seek(0)
        return None

# ============================================================================
# API CLIENT
# ============================================================================

class FileUploadAPIClient:
    """API client for file upload operations."""

    def __init__(self, token: str):
        self.base_url = API_BASE_URL
        self.token = token

    def _get_headers(self, include_content_type: bool = True) -> Dict[str, str]:
        """Get headers with authentication."""
        headers = {'Authorization': f'Bearer {self.token}'}
        if include_content_type:
            headers['Content-Type'] = 'application/json'
        return headers

    def get_articles(self) -> Dict:
        """Fetch all articles."""
        response = requests.get(
            f"{self.base_url}/articles",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_article(self, article_id: int) -> Dict:
        """Fetch a single article."""
        response = requests.get(
            f"{self.base_url}/articles/{article_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 5: upload_article_image method
    def upload_article_image(self, article_id: int, uploaded_file) -> Dict:
        """Upload image for an article."""
        # Reset file pointer to beginning
        uploaded_file.seek(0)

        # Prepare multipart file upload
        files = {
            'file': (uploaded_file.name, uploaded_file, uploaded_file.type)
        }

        # Make request (don't include Content-Type for multipart)
        response = requests.post(
            f"{self.base_url}/articles/{article_id}/image",
            files=files,
            headers=self._get_headers(include_content_type=False)
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

# Initialize and check authentication
init_session_state()
require_auth()

# Create API client
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

# SOLUTION 6: Fetch and display articles
try:
    response = api.get_articles()
    all_articles = response['articles']

    # Filter user's articles
    my_articles = [a for a in all_articles if a['author']['id'] == st.session_state.user['id']]

    if my_articles:
        article_options = {
            f"{article['title']}": article['id']
            for article in my_articles
        }

        selected_title = st.selectbox(
            "Choose an article:",
            options=list(article_options.keys())
        )

        st.session_state.selected_article_id = article_options[selected_title]

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

    # SOLUTION 7: File uploader widget
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=ALLOWED_IMAGE_TYPES,
        help=f"Max size: {MAX_FILE_SIZE_MB}MB. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
    )

    if uploaded_file is not None:

        # ====================================================================
        # VALIDATION
        # ====================================================================

        st.subheader("✅ Validation")

        # SOLUTION 8: Validate file size
        size_valid, size_error = validate_file_size(uploaded_file)
        if size_valid:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.success(f"✅ File size OK ({file_size_mb:.2f}MB)")
        else:
            st.error(size_error)

        # SOLUTION 9: Validate file type
        type_valid, type_error = validate_file_type(uploaded_file)
        if type_valid:
            st.success(f"✅ File type OK ({uploaded_file.name.split('.')[-1].lower()})")
        else:
            st.error(type_error)

        # SOLUTION 10: Validate image content
        content_valid, content_error = validate_image_content(uploaded_file)
        if content_valid:
            st.success("✅ Valid image file")
        else:
            st.error(content_error)

        # SOLUTION 11: Check if all validations passed
        all_valid = size_valid and type_valid and content_valid

        if all_valid:

            # ================================================================
            # IMAGE PREVIEW
            # ================================================================

            st.subheader("👁️ Preview")

            # SOLUTION 12: Display image preview
            st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

            # Get and display image info
            info = get_image_info(uploaded_file)
            if info:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Width", f"{info['width']}px")
                with col2:
                    st.metric("Height", f"{info['height']}px")
                with col3:
                    st.metric("Format", info['format'])
                with col4:
                    st.metric("Size", f"{info['size_mb']:.2f}MB")

            # ================================================================
            # UPLOAD TO BACKEND
            # ================================================================

            st.subheader("📤 Upload")

            # SOLUTION 13: Upload button and handling
            if st.button("📤 Upload Image to Article", type="primary"):
                try:
                    with st.spinner("Uploading image..."):
                        result = api.upload_article_image(
                            st.session_state.selected_article_id,
                            uploaded_file
                        )

                    st.success("✅ Image uploaded successfully!")
                    st.info(f"Image URL: {result['image_url']}")

                    # Display uploaded image
                    st.image(result['image_url'], caption="Uploaded Image", use_container_width=True)

                    st.balloons()

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
    # SOLUTION 14: Display current article image
    try:
        article = api.get_article(st.session_state.selected_article_id)

        if article.get('image_url'):
            st.image(article['image_url'], caption=f"Current image for: {article['title']}", use_container_width=True)
            st.caption(f"Image URL: {article['image_url']}")
        else:
            st.info("📭 No image uploaded for this article yet")

    except Exception as e:
        st.error(f"❌ Error loading article: {e}")

st.divider()

# ============================================================================
# IMAGE UPLOAD BEST PRACTICES
# ============================================================================

st.header("📚 Best Practices")

with st.expander("Learn about file upload best practices"):
    st.markdown("""
    ### Client-Side Validation

    Always validate files before uploading:
    1. **File size:** Prevent large uploads that waste bandwidth
    2. **File type:** Check extension matches expected types
    3. **File content:** Verify file is actually the claimed type

    ### Server-Side Validation

    Never trust client validation alone:
    - Backend must also validate
    - Check file size, type, content
    - Scan for malware in production

    ### User Experience

    - Show clear error messages
    - Display upload progress
    - Preview before uploading
    - Confirm successful upload

    ### Security Considerations

    1. **Validate file type:** Don't trust extension alone
    2. **Limit file size:** Prevent DoS attacks
    3. **Scan content:** Check for malware
    4. **Rename files:** Don't use user-provided filenames directly
    5. **Store securely:** Use proper permissions

    ### Performance

    - Resize large images before upload
    - Use appropriate formats (JPEG for photos, PNG for graphics)
    - Compress images when possible
    - Consider using CDN for serving images

    ### Code Example

    ```python
    # Good validation pattern
    def validate_upload(file):
        # Check size
        if file.size > MAX_SIZE:
            return False, "File too large"

        # Check type
        ext = file.name.split('.')[-1]
        if ext not in ALLOWED_TYPES:
            return False, "Invalid file type"

        # Check content
        try:
            img = Image.open(file)
            img.verify()
        except:
            return False, "Invalid image file"

        return True, None
    ```
    """)

# ============================================================================
# COMPLETION CHECK
# ============================================================================

st.divider()

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

You now have the skills to build complete full-stack applications with:
- Streamlit frontend
- Flask backend integration
- Authentication with JWT
- CRUD operations
- File uploads
- Data validation
- Error handling

**Next Steps:**
- Review solutions on solutions branch
- Build your own full-stack project
- Explore advanced Streamlit features
- Learn about deployment
""")

# ============================================================================
# TESTING CHECKLIST
# ============================================================================

with st.expander("✅ Testing Checklist"):
    st.markdown("""
    Test all file upload scenarios:

    **Valid Uploads:**
    - [x] Small image (<1MB) uploads successfully
    - [x] Large image (3-4MB) uploads successfully
    - [x] JPG format works
    - [x] PNG format works
    - [x] GIF format works

    **Validation:**
    - [x] File > 5MB rejected
    - [x] Non-image file rejected
    - [x] Invalid extension rejected
    - [x] Corrupted image rejected
    - [x] Error messages are clear

    **Preview:**
    - [x] Image preview displays
    - [x] Image info shows correctly
    - [x] Preview updates with new file

    **Backend Integration:**
    - [x] Upload button works
    - [x] Success message appears
    - [x] Image URL returned
    - [x] Image appears in article
    - [x] Current image displays

    **Error Handling:**
    - [x] Network errors handled
    - [x] Backend errors handled
    - [x] Validation errors clear
    - [x] App doesn't crash
    """)
