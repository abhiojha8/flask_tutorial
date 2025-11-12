"""
Exercise 5: File Upload & Validation 🔴
Difficulty: Advanced
Estimated Time: 90 minutes

GOAL:
Build a file upload system with proper validation, preview, and integration
with the backend API.

LEARNING OBJECTIVES:
- Handle file uploads in Streamlit
- Validate file size and type
- Preview images before upload
- Make multipart/form-data requests
- Process uploaded files
- Integrate with backend file upload endpoint

REQUIREMENTS:
1. Create file upload widget
2. Validate file size (max 5MB)
3. Validate file type (images only)
4. Show image preview
5. Upload to backend
6. Display uploaded images
7. Handle errors gracefully

INSTRUCTIONS:
1. Look for TODO comments
2. Implement the required functionality
3. Run: streamlit run exercise_5_file_upload.py
4. Login first (john.doe@example.com / password123)
5. Create or select an article
6. Upload an image

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

# TODO 1: Implement validate_file_size() function
# This should:
# - Accept uploaded_file parameter
# - Check file size in MB
# - Return (is_valid, error_message) tuple
# - is_valid is True if size <= MAX_FILE_SIZE_MB
# - error_message is string describing the issue or None
#
# Hint: file_size_mb = uploaded_file.size / (1024 * 1024)

def validate_file_size(uploaded_file) -> tuple[bool, Optional[str]]:
    """
    Validate file size is within limits.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        (is_valid, error_message) tuple
    """
    # YOUR CODE HERE
    pass

# TODO 2: Implement validate_file_type() function
# This should:
# - Accept uploaded_file parameter
# - Extract file extension from name
# - Check if extension in ALLOWED_IMAGE_TYPES
# - Return (is_valid, error_message) tuple
#
# Hint: file.name.split('.')[-1].lower()

def validate_file_type(uploaded_file) -> tuple[bool, Optional[str]]:
    """
    Validate file type is an allowed image format.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        (is_valid, error_message) tuple
    """
    # YOUR CODE HERE
    pass

# TODO 3: Implement validate_image_content() function
# This should:
# - Accept uploaded_file parameter
# - Try to open as image using PIL
# - Check if valid image format
# - Return (is_valid, error_message) tuple
# - Return (False, error) if PIL not available
#
# Hint: Use Image.open(BytesIO(uploaded_file.read()))
# Hint: Call uploaded_file.seek(0) after reading to reset

def validate_image_content(uploaded_file) -> tuple[bool, Optional[str]]:
    """
    Validate file is actually a valid image using PIL.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        (is_valid, error_message) tuple
    """
    if not PIL_AVAILABLE:
        return False, "PIL not installed"

    # YOUR CODE HERE
    pass

# TODO 4: Implement get_image_info() function
# This should:
# - Accept uploaded_file parameter
# - Open image with PIL
# - Extract image info: width, height, format, mode
# - Return dict with image info
# - Return None if error or PIL not available
#
# Hint: img = Image.open(BytesIO(uploaded_file.read()))
# Hint: img.size gives (width, height)
# Hint: Reset file pointer with uploaded_file.seek(0)

def get_image_info(uploaded_file) -> Optional[Dict]:
    """
    Extract image information using PIL.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Dict with image info or None if error
    """
    if not PIL_AVAILABLE:
        return None

    # YOUR CODE HERE
    pass

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

    # TODO 5: Implement upload_article_image() method
    # This should:
    # - Accept article_id and uploaded_file parameters
    # - Prepare multipart/form-data request
    # - Create files dict: {'file': (filename, file_content, content_type)}
    # - Make POST request to /articles/{article_id}/image
    # - Include Authorization header (NOT Content-Type for multipart)
    # - Return response JSON
    #
    # Hint: files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
    # Hint: Use headers without Content-Type for multipart
    # Hint: requests.post(url, files=files, headers=...)

    def upload_article_image(self, article_id: int, uploaded_file) -> Dict:
        """
        Upload image for an article.

        Args:
            article_id: Article ID
            uploaded_file: Streamlit UploadedFile object

        Returns:
            Response dict with image_url
        """
        # YOUR CODE HERE
        pass

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

# TODO 6: Fetch and display articles for selection
# - Fetch user's articles using api.get_articles()
# - Filter to show only user's articles
# - Create selectbox with article titles
# - Store selected article_id in session state
#
# Hint: Filter where article['author']['id'] == st.session_state.user['id']
# Hint: Use st.selectbox()

# YOUR CODE HERE
try:
    response = api.get_articles()
    all_articles = response['articles']

    # Filter user's articles
    my_articles = [a for a in all_articles if a['author']['id'] == st.session_state.user['id']]

    if my_articles:
        # YOUR CODE HERE - Create selectbox
        pass
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

    # TODO 7: Create file uploader widget
    # - Use st.file_uploader()
    # - Accept image types
    # - Show help text with requirements
    #
    # Hint: type=['jpg', 'jpeg', 'png', 'gif']
    # Hint: help=f"Max size: {MAX_FILE_SIZE_MB}MB"

    uploaded_file = None  # YOUR CODE HERE - Replace with actual file_uploader

    if uploaded_file is not None:

        # ====================================================================
        # VALIDATION
        # ====================================================================

        st.subheader("✅ Validation")

        # TODO 8: Validate file size
        # - Call validate_file_size()
        # - Show success or error based on result
        #
        # Hint: Use st.success() or st.error()

        # YOUR CODE HERE
        pass

        # TODO 9: Validate file type
        # - Call validate_file_type()
        # - Show success or error based on result

        # YOUR CODE HERE
        pass

        # TODO 10: Validate image content
        # - Call validate_image_content()
        # - Show success or error based on result

        # YOUR CODE HERE
        pass

        # Check if all validations passed
        # TODO 11: Combine all validation results
        # Only proceed if all validations passed

        all_valid = False  # YOUR CODE HERE - Combine validation results

        if all_valid:

            # ================================================================
            # IMAGE PREVIEW
            # ================================================================

            st.subheader("👁️ Preview")

            # TODO 12: Display image preview
            # - Show the uploaded image
            # - Display image info (dimensions, format, size)
            #
            # Hint: Use st.image(uploaded_file)
            # Hint: Use get_image_info() for details

            # YOUR CODE HERE
            pass

            # ================================================================
            # UPLOAD TO BACKEND
            # ================================================================

            st.subheader("📤 Upload")

            # TODO 13: Create upload button and handle upload
            # - Add button "Upload Image"
            # - On click:
            #   - Show spinner "Uploading..."
            #   - Call api.upload_article_image()
            #   - Show success message with image URL
            #   - Show the uploaded image
            #   - Handle errors
            #
            # Hint: Use st.button()
            # Hint: Wrap API call in try/except

            # YOUR CODE HERE
            pass

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
    # TODO 14: Fetch and display current article image
    # - Fetch article using api.get_article()
    # - Check if image_url exists
    # - Display current image
    # - Show message if no image
    #
    # Hint: Check if article.get('image_url')
    # Hint: Use st.image() to display

    # YOUR CODE HERE
    pass

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
    - [ ] Small image (<1MB) uploads successfully
    - [ ] Large image (3-4MB) uploads successfully
    - [ ] JPG format works
    - [ ] PNG format works
    - [ ] GIF format works

    **Validation:**
    - [ ] File > 5MB rejected
    - [ ] Non-image file rejected
    - [ ] Invalid extension rejected
    - [ ] Corrupted image rejected
    - [ ] Error messages are clear

    **Preview:**
    - [ ] Image preview displays
    - [ ] Image info shows correctly
    - [ ] Preview updates with new file

    **Backend Integration:**
    - [ ] Upload button works
    - [ ] Success message appears
    - [ ] Image URL returned
    - [ ] Image appears in article
    - [ ] Current image displays

    **Error Handling:**
    - [ ] Network errors handled
    - [ ] Backend errors handled
    - [ ] Validation errors clear
    - [ ] App doesn't crash
    """)
