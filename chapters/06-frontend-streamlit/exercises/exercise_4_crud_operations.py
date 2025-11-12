"""
Exercise 4: CRUD Operations 🟡
Difficulty: Intermediate
Estimated Time: 60 minutes

GOAL:
Build a complete task manager application with Create, Read, Update, and Delete
operations, demonstrating full CRUD functionality with authentication.

LEARNING OBJECTIVES:
- Implement Create operation with forms
- Implement Read operation with data display
- Implement Update operation with edit forms
- Implement Delete operation with confirmation
- Manage state across operations
- Handle validation and errors

REQUIREMENTS:
1. View all tasks (using articles as tasks)
2. Create new tasks
3. Edit existing tasks
4. Delete tasks
5. Require authentication for all operations
6. Validate form inputs

INSTRUCTIONS:
1. Look for TODO comments
2. Implement the required functionality
3. Run: streamlit run exercise_4_crud_operations.py
4. Login first (john.doe@example.com / password123)
5. Test all CRUD operations

NOTE: We're using articles as "tasks" to reuse the backend API
"""

import streamlit as st
import requests
from typing import Dict, Optional

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# HELPER FUNCTIONS (from previous exercises)
# ============================================================================

def init_session_state():
    """Initialize session state for authentication and app state."""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None

    # TODO 1: Initialize additional session state variables
    # Add:
    # - 'edit_task_id' : None (for tracking which task is being edited)
    # - 'view_mode' : 'list' (for tracking current view: 'list', 'create', 'edit')
    #
    # Hint: Same pattern as token and user

    # YOUR CODE HERE


def is_authenticated() -> bool:
    """Check if user is logged in."""
    return st.session_state.token is not None and st.session_state.user is not None

def require_auth():
    """Redirect to login if not authenticated."""
    if not is_authenticated():
        st.warning("⚠️ You must be logged in to use this app.")
        st.info("Please login below:")

        # Simple login form
        with st.form("quick_login"):
            email = st.text_input("Email", value="john.doe@example.com")
            password = st.text_input("Password", type="password", value="password123")
            submit = st.form_submit_button("Login")

            if submit:
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
# API CLIENT
# ============================================================================

class TaskAPIClient:
    """API client for task operations (using articles as tasks)."""

    def __init__(self, token: str):
        self.base_url = API_BASE_URL
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    # TODO 2: Implement get_tasks() method
    # This should:
    # - Make GET request to /articles
    # - Include auth headers
    # - Return the response JSON
    #
    # Hint: requests.get(url, headers=self._get_headers())

    def get_tasks(self) -> Dict:
        """Fetch all tasks (articles)."""
        # YOUR CODE HERE
        pass

    # TODO 3: Implement get_task() method
    # This should:
    # - Accept task_id parameter
    # - Make GET request to /articles/{task_id}
    # - Include auth headers
    # - Return the response JSON
    #
    # Hint: Similar to get_tasks but with ID in URL

    def get_task(self, task_id: int) -> Dict:
        """Fetch a single task by ID."""
        # YOUR CODE HERE
        pass

    # TODO 4: Implement create_task() method
    # This should:
    # - Accept task_data dictionary
    # - Make POST request to /articles
    # - Include auth headers
    # - Send task_data as JSON body
    # - Return the response JSON
    #
    # Hint: requests.post(url, json=task_data, headers=self._get_headers())

    def create_task(self, task_data: Dict) -> Dict:
        """Create a new task."""
        # YOUR CODE HERE
        pass

    # TODO 5: Implement update_task() method
    # This should:
    # - Accept task_id and task_data
    # - Make PUT request to /articles/{task_id}
    # - Include auth headers
    # - Send task_data as JSON body
    # - Return the response JSON
    #
    # Hint: Use requests.put()

    def update_task(self, task_id: int, task_data: Dict) -> Dict:
        """Update an existing task."""
        # YOUR CODE HERE
        pass

    # TODO 6: Implement delete_task() method
    # This should:
    # - Accept task_id
    # - Make DELETE request to /articles/{task_id}
    # - Include auth headers
    # - Return the response JSON
    #
    # Hint: Use requests.delete()

    def delete_task(self, task_id: int) -> Dict:
        """Delete a task."""
        # YOUR CODE HERE
        pass

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Exercise 4 | CRUD Operations",
    page_icon="✅",
    layout="wide"
)

# Initialize and check authentication
init_session_state()
require_auth()

# Create API client
api = TaskAPIClient(st.session_state.token)

# ============================================================================
# HEADER
# ============================================================================

st.title("✅ Task Manager")
st.caption(f"Welcome, {st.session_state.user['name']}!")

st.divider()

# ============================================================================
# SIDEBAR - VIEW CONTROLS
# ============================================================================

with st.sidebar:
    st.subheader("🎯 Actions")

    # TODO 7: Create buttons to switch between views
    # Add buttons for:
    # - "📋 View All Tasks" - sets view_mode to 'list'
    # - "➕ Create New Task" - sets view_mode to 'create'
    #
    # Hint: On button click, update st.session_state.view_mode and st.rerun()

    # YOUR CODE HERE
    pass

    st.divider()

    st.subheader("👤 User")
    st.write(f"**{st.session_state.user['name']}**")
    st.caption(st.session_state.user['email'])

    if st.button("🚪 Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

# ============================================================================
# MAIN CONTENT - ROUTE BY VIEW MODE
# ============================================================================

# TODO 8: Route to different views based on view_mode
# Check st.session_state.view_mode and show appropriate content:
# - 'list': Show all tasks
# - 'create': Show create form
# - 'edit': Show edit form
#
# Hint: Use if/elif/else

# YOUR CODE HERE
view_mode = st.session_state.get('view_mode', 'list')

# ============================================================================
# VIEW: LIST ALL TASKS
# ============================================================================

if view_mode == 'list':
    st.header("📋 All Tasks")

    # TODO 9: Fetch and display all tasks
    # - Use spinner "Loading tasks..."
    # - Fetch tasks using api.get_tasks()
    # - Display each task with:
    #   - Title
    #   - Status (published = completed, not published = pending)
    #   - Content preview
    #   - Edit button
    #   - Delete button
    # - Handle errors
    #
    # Hint: Use try/except
    # Hint: Loop through tasks and use st.container()

    # YOUR CODE HERE
    pass

# ============================================================================
# VIEW: CREATE TASK
# ============================================================================

elif view_mode == 'create':
    st.header("➕ Create New Task")

    # TODO 10: Create task creation form
    # Form should have:
    # - Title input (required, max 200 chars)
    # - Description textarea (required, min 10 chars)
    # - Status checkbox (completed/pending)
    # - Submit button
    #
    # On submit:
    # - Validate inputs
    # - Create task data dict (title, content, published)
    # - Call api.create_task()
    # - Show success message
    # - Switch back to list view
    # - Handle errors
    #
    # Hint: Use st.form()
    # Hint: Map article fields: title->title, content->description, published->completed

    # YOUR CODE HERE
    pass

    # Cancel button
    if st.button("Cancel"):
        st.session_state.view_mode = 'list'
        st.rerun()

# ============================================================================
# VIEW: EDIT TASK
# ============================================================================

elif view_mode == 'edit':
    st.header("✏️ Edit Task")

    task_id = st.session_state.get('edit_task_id')

    if not task_id:
        st.error("No task selected for editing")
        if st.button("Back to List"):
            st.session_state.view_mode = 'list'
            st.rerun()
    else:
        # TODO 11: Fetch task and show edit form
        # - Fetch the task using api.get_task(task_id)
        # - Show form pre-filled with task data
        # - Allow editing title, content, status
        # - On submit:
        #   - Validate inputs
        #   - Call api.update_task()
        #   - Show success message
        #   - Switch back to list view
        # - Handle errors
        #
        # Hint: Similar to create form but with existing values
        # Hint: Use value= parameter to pre-fill fields

        # YOUR CODE HERE
        pass

        # Cancel button
        if st.button("Cancel"):
            st.session_state.view_mode = 'list'
            st.session_state.edit_task_id = None
            st.rerun()

# ============================================================================
# DELETE CONFIRMATION MODAL
# ============================================================================

# TODO 12: Create a section for delete confirmations
# This can be shown in any view mode
# If a task is marked for deletion:
# - Show warning message
# - Show task details
# - Show "Confirm Delete" button
# - Show "Cancel" button
#
# Hint: Use a session state variable like 'delete_task_id'
# Hint: Use st.warning() for the confirmation

# YOUR CODE HERE


# ============================================================================
# STATISTICS
# ============================================================================

st.divider()
st.subheader("📊 Statistics")

# TODO 13: Fetch tasks and show statistics
# Display:
# - Total tasks
# - Completed tasks (published)
# - Pending tasks (not published)
# Use columns for layout
#
# Hint: Fetch tasks and count
# Hint: Use st.columns(3)

# YOUR CODE HERE


# ============================================================================
# COMPLETION CHECK
# ============================================================================

st.divider()

st.success("""
✅ **Exercise 4 Complete!**

You've learned how to:
- Implement Create operation with forms
- Implement Read operation with data fetching
- Implement Update operation with edit forms
- Implement Delete operation with confirmation
- Manage application state across operations
- Handle validation and errors
- Build a complete CRUD application

**Next Step:** Move on to Exercise 5 for file upload!
""")

# ============================================================================
# TESTING CHECKLIST
# ============================================================================

with st.expander("✅ Testing Checklist"):
    st.markdown("""
    Test all CRUD operations:

    **Create:**
    - [ ] Can create new task
    - [ ] Validation works (required fields)
    - [ ] Success message appears
    - [ ] Redirects to list view
    - [ ] New task appears in list

    **Read:**
    - [ ] All tasks display correctly
    - [ ] Task details are accurate
    - [ ] Status shows correctly
    - [ ] Loading spinner appears

    **Update:**
    - [ ] Can click edit on a task
    - [ ] Form pre-fills with current data
    - [ ] Can modify fields
    - [ ] Changes save correctly
    - [ ] Updated data shows in list

    **Delete:**
    - [ ] Can click delete on a task
    - [ ] Confirmation appears
    - [ ] Can confirm delete
    - [ ] Can cancel delete
    - [ ] Task removed from list

    **Error Handling:**
    - [ ] Errors show user-friendly messages
    - [ ] App doesn't crash on errors
    - [ ] Invalid data rejected
    """)
