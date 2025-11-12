"""
Create/Edit Article Page
Allows authenticated users to create new articles or edit existing ones
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from config import API_BASE_URL, MAX_FILE_SIZE_MB, ALLOWED_IMAGE_TYPES
from utils.auth import init_session_state, require_auth
from utils.api_client import BlogAPIClient, handle_api_error

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Create Article | Blog App",
    page_icon="✍️",
    layout="wide"
)

# Initialize session state
init_session_state()

# Require authentication
require_auth()

# ============================================================================
# EDIT MODE CHECK
# ============================================================================

edit_mode = False
article_to_edit = None

if 'edit_article_id' in st.session_state and st.session_state.edit_article_id:
    edit_mode = True
    article_id = st.session_state.edit_article_id

    # Fetch article to edit
    try:
        api = BlogAPIClient(API_BASE_URL, st.session_state.token)
        article_to_edit = api.get_article(article_id)

        # Verify ownership
        if article_to_edit['author']['id'] != st.session_state.user['id']:
            st.error("❌ You can only edit your own articles!")
            st.stop()

    except Exception as e:
        handle_api_error(e)
        st.stop()

# ============================================================================
# PAGE HEADER
# ============================================================================

if edit_mode:
    st.title("✏️ Edit Article")
    st.caption(f"Editing: {article_to_edit['title']}")
else:
    st.title("✍️ Create New Article")
    st.caption("Share your thoughts with the world!")

st.divider()

# ============================================================================
# ARTICLE FORM
# ============================================================================

with st.form("article_form", clear_on_submit=not edit_mode):
    # Title
    title = st.text_input(
        "Article Title *",
        value=article_to_edit['title'] if edit_mode else "",
        placeholder="Enter a compelling title...",
        max_chars=200
    )

    # Content
    content = st.text_area(
        "Article Content *",
        value=article_to_edit['content'] if edit_mode else "",
        placeholder="Write your article content here...\n\nYou can use markdown formatting!",
        height=300
    )

    # Category
    categories = ["Technology", "Science", "Business", "Health", "Sports", "Other"]
    current_category = article_to_edit.get('category', '') if edit_mode else ''

    if current_category and current_category in categories:
        category_index = categories.index(current_category)
    else:
        category_index = 0

    category = st.selectbox(
        "Category",
        options=categories,
        index=category_index
    )

    # Tags
    tags_input = st.text_input(
        "Tags (comma-separated)",
        value=", ".join(article_to_edit.get('tags', [])) if edit_mode else "",
        placeholder="python, web development, tutorial"
    )

    # Published status
    col1, col2 = st.columns(2)

    with col1:
        published = st.checkbox(
            "Publish immediately",
            value=article_to_edit['published'] if edit_mode else False,
            help="Uncheck to save as draft"
        )

    with col2:
        st.caption("💡 You can always publish drafts later")

    st.divider()

    # Submit buttons
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        submit = st.form_submit_button(
            "💾 Update Article" if edit_mode else "📝 Create Article",
            type="primary"
        )

    with col2:
        if edit_mode:
            cancel = st.form_submit_button("Cancel")
        else:
            cancel = False

    # Form submission
    if submit:
        # Validation
        errors = []

        if not title or not title.strip():
            errors.append("❌ Title is required")

        if len(title) < 5:
            errors.append("❌ Title must be at least 5 characters")

        if not content or not content.strip():
            errors.append("❌ Content is required")

        if len(content) < 50:
            errors.append("❌ Content must be at least 50 characters")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # Prepare article data
            article_data = {
                'title': title.strip(),
                'content': content.strip(),
                'category': category if category != "Other" else None,
                'published': published
            }

            # Parse tags
            if tags_input:
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                article_data['tags'] = tags

            try:
                api = BlogAPIClient(API_BASE_URL, st.session_state.token)

                if edit_mode:
                    # Update existing article
                    updated_article = api.update_article(article_id, article_data)
                    st.success("✅ Article updated successfully!")

                    # Clear edit mode
                    st.session_state.edit_article_id = None

                else:
                    # Create new article
                    new_article = api.create_article(article_data)
                    st.success("✅ Article created successfully!")
                    st.balloons()

                # Redirect after short delay
                st.info("Redirecting to articles...")
                import time
                time.sleep(2)
                st.switch_page("pages/1_📝_Articles.py")

            except Exception as e:
                handle_api_error(e)

    if cancel:
        st.session_state.edit_article_id = None
        st.rerun()

# ============================================================================
# IMAGE UPLOAD (for existing articles)
# ============================================================================

if edit_mode and article_to_edit:
    st.divider()
    st.subheader("🖼️ Article Image")

    # Show current image
    if article_to_edit.get('image_url'):
        st.image(article_to_edit['image_url'], width=300)
        st.caption("Current article image")
    else:
        st.info("No image uploaded yet")

    # Upload new image
    st.markdown("**Upload New Image**")

    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=ALLOWED_IMAGE_TYPES,
        help=f"Max file size: {MAX_FILE_SIZE_MB}MB"
    )

    if uploaded_file:
        # File size validation
        file_size_mb = uploaded_file.size / (1024 * 1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"❌ File size ({file_size_mb:.2f}MB) exceeds maximum ({MAX_FILE_SIZE_MB}MB)")
        else:
            # Preview
            st.image(uploaded_file, width=300)
            st.caption(f"Preview: {uploaded_file.name} ({file_size_mb:.2f}MB)")

            if st.button("📤 Upload Image", type="primary"):
                try:
                    api = BlogAPIClient(API_BASE_URL, st.session_state.token)

                    with st.spinner("Uploading image..."):
                        response = api.upload_article_image(article_id, uploaded_file)

                    st.success("✅ Image uploaded successfully!")
                    st.rerun()

                except Exception as e:
                    handle_api_error(e)

# ============================================================================
# DELETE ARTICLE (for edit mode)
# ============================================================================

if edit_mode and article_to_edit:
    st.divider()
    st.subheader("🗑️ Danger Zone")

    with st.expander("Delete Article", expanded=False):
        st.warning("⚠️ This action cannot be undone!")

        confirm_delete = st.checkbox("I understand this will permanently delete the article")

        if confirm_delete:
            if st.button("🗑️ Delete Article", type="primary"):
                try:
                    api = BlogAPIClient(API_BASE_URL, st.session_state.token)
                    api.delete_article(article_id)

                    st.success("✅ Article deleted successfully!")
                    st.session_state.edit_article_id = None

                    import time
                    time.sleep(2)
                    st.switch_page("app.py")

                except Exception as e:
                    handle_api_error(e)

# ============================================================================
# WRITING TIPS
# ============================================================================

st.divider()

with st.expander("💡 Writing Tips", expanded=False):
    st.markdown("""
    ### Tips for Great Articles

    **Title:**
    - Keep it clear and compelling
    - Use keywords that readers might search for
    - Aim for 5-10 words

    **Content:**
    - Start with a strong introduction
    - Use headings to organize sections
    - Include examples and code snippets
    - End with a clear conclusion

    **Formatting:**
    - Use **bold** for emphasis
    - Use `code blocks` for technical terms
    - Add bullet points for lists
    - Include images to illustrate points

    **Markdown Support:**
    ```markdown
    # Heading 1
    ## Heading 2
    ### Heading 3

    **bold text**
    *italic text*

    - Bullet point
    - Another point

    `inline code`

    ```python
    # Code block
    def hello():
        print("Hello!")
    ```
    ```

    **Tags:**
    - Use 3-5 relevant tags
    - Keep them lowercase
    - Use common terms readers search for
    """)

# ============================================================================
# NAVIGATION
# ============================================================================

st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🏠 Back to Home"):
        if edit_mode:
            st.session_state.edit_article_id = None
        st.switch_page("app.py")

with col2:
    if st.button("📝 View All Articles"):
        if edit_mode:
            st.session_state.edit_article_id = None
        st.switch_page("pages/1_📝_Articles.py")
