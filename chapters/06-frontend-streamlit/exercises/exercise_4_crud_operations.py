"""
Exercise 4: CRUD Operations 🟡
Difficulty: Intermediate
Estimated Time: 60 minutes

SOLUTION
"""

import streamlit as st
import requests
from typing import Dict, Optional

# Backend API URL
API_BASE_URL = 'http://localhost:5000/api'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_session_state():
    """Initialize session state for authentication and app state."""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None

    # SOLUTION 1: Additional session state variables
    if 'edit_task_id' not in st.session_state:
        st.session_state.edit_task_id = None
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'list'
    if 'delete_task_id' not in st.session_state:
        st.session_state.delete_task_id = None

def is_authenticated() -> bool:
    """Check if user is logged in."""
    return st.session_state.token is not None and st.session_state.user is not None

def require_auth():
    """Redirect to login if not authenticated."""
    if not is_authenticated():
        st.warning("⚠️ You must be logged in to use this app.")
        st.info("Please login below:")

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

    # SOLUTION 2: get_tasks method
    def get_tasks(self) -> Dict:
        """Fetch all tasks (articles)."""
        response = requests.get(
            f"{self.base_url}/articles",
            headers=self._get_headers(),
            params={'per_page': 100}
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 3: get_task method
    def get_task(self, task_id: int) -> Dict:
        """Fetch a single task by ID."""
        response = requests.get(
            f"{self.base_url}/articles/{task_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 4: create_task method
    def create_task(self, task_data: Dict) -> Dict:
        """Create a new task."""
        response = requests.post(
            f"{self.base_url}/articles",
            headers=self._get_headers(),
            json=task_data
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 5: update_task method
    def update_task(self, task_id: int, task_data: Dict) -> Dict:
        """Update an existing task."""
        response = requests.put(
            f"{self.base_url}/articles/{task_id}",
            headers=self._get_headers(),
            json=task_data
        )
        response.raise_for_status()
        return response.json()

    # SOLUTION 6: delete_task method
    def delete_task(self, task_id: int) -> Dict:
        """Delete a task."""
        response = requests.delete(
            f"{self.base_url}/articles/{task_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

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

    # SOLUTION 7: View mode buttons
    if st.button("📋 View All Tasks", use_container_width=True):
        st.session_state.view_mode = 'list'
        st.session_state.edit_task_id = None
        st.rerun()

    if st.button("➕ Create New Task", use_container_width=True):
        st.session_state.view_mode = 'create'
        st.session_state.edit_task_id = None
        st.rerun()

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

# SOLUTION 8: Route based on view_mode
view_mode = st.session_state.get('view_mode', 'list')

# ============================================================================
# VIEW: LIST ALL TASKS
# ============================================================================

if view_mode == 'list':
    st.header("📋 All Tasks")

    # SOLUTION 9: Fetch and display tasks
    try:
        with st.spinner("Loading tasks..."):
            response = api.get_tasks()
            all_tasks = response['articles']

            # Filter to user's tasks only
            my_tasks = [t for t in all_tasks if t['author']['id'] == st.session_state.user['id']]

        if my_tasks:
            for task in my_tasks:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.subheader(f"{'✅' if task['published'] else '⏳'} {task['title']}")
                        content_preview = task['content'][:100] + "..." if len(task['content']) > 100 else task['content']
                        st.write(content_preview)

                        status = "Completed" if task['published'] else "Pending"
                        st.caption(f"Status: **{status}** | Created: {task['created_at'][:10]}")

                    with col2:
                        if st.button("✏️ Edit", key=f"edit_{task['id']}"):
                            st.session_state.view_mode = 'edit'
                            st.session_state.edit_task_id = task['id']
                            st.rerun()

                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                            st.session_state.delete_task_id = task['id']
                            st.rerun()

                    st.divider()
        else:
            st.info("📭 No tasks yet. Create your first task!")

    except Exception as e:
        st.error(f"❌ Error loading tasks: {e}")

# ============================================================================
# VIEW: CREATE TASK
# ============================================================================

elif view_mode == 'create':
    st.header("➕ Create New Task")

    # SOLUTION 10: Create task form
    with st.form("create_task_form"):
        title = st.text_input(
            "Task Title *",
            placeholder="Enter task title...",
            max_chars=200
        )

        description = st.text_area(
            "Description *",
            placeholder="Describe your task...",
            height=150
        )

        completed = st.checkbox("Mark as completed")

        submit = st.form_submit_button("✅ Create Task", type="primary")

        if submit:
            # Validation
            errors = []

            if not title or not title.strip():
                errors.append("❌ Title is required")
            elif len(title) < 3:
                errors.append("❌ Title must be at least 3 characters")

            if not description or not description.strip():
                errors.append("❌ Description is required")
            elif len(description) < 10:
                errors.append("❌ Description must be at least 10 characters")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create task
                task_data = {
                    'title': title.strip(),
                    'content': description.strip(),
                    'published': completed
                }

                try:
                    with st.spinner("Creating task..."):
                        new_task = api.create_task(task_data)

                    st.success(f"✅ Task '{new_task['title']}' created successfully!")
                    st.balloons()

                    # Switch to list view
                    st.session_state.view_mode = 'list'
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error creating task: {e}")

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
        # SOLUTION 11: Fetch and edit task
        try:
            with st.spinner("Loading task..."):
                task = api.get_task(task_id)

            # Verify ownership
            if task['author']['id'] != st.session_state.user['id']:
                st.error("❌ You can only edit your own tasks!")
                if st.button("Back to List"):
                    st.session_state.view_mode = 'list'
                    st.session_state.edit_task_id = None
                    st.rerun()
            else:
                # Edit form
                with st.form("edit_task_form"):
                    title = st.text_input(
                        "Task Title *",
                        value=task['title'],
                        max_chars=200
                    )

                    description = st.text_area(
                        "Description *",
                        value=task['content'],
                        height=150
                    )

                    completed = st.checkbox("Mark as completed", value=task['published'])

                    submit = st.form_submit_button("💾 Save Changes", type="primary")

                    if submit:
                        # Validation
                        errors = []

                        if not title or not title.strip():
                            errors.append("❌ Title is required")
                        elif len(title) < 3:
                            errors.append("❌ Title must be at least 3 characters")

                        if not description or not description.strip():
                            errors.append("❌ Description is required")
                        elif len(description) < 10:
                            errors.append("❌ Description must be at least 10 characters")

                        if errors:
                            for error in errors:
                                st.error(error)
                        else:
                            # Update task
                            task_data = {
                                'title': title.strip(),
                                'content': description.strip(),
                                'published': completed
                            }

                            try:
                                with st.spinner("Updating task..."):
                                    updated_task = api.update_task(task_id, task_data)

                                st.success(f"✅ Task '{updated_task['title']}' updated successfully!")

                                # Switch to list view
                                st.session_state.view_mode = 'list'
                                st.session_state.edit_task_id = None
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error updating task: {e}")

        except Exception as e:
            st.error(f"❌ Error loading task: {e}")

        if st.button("Cancel"):
            st.session_state.view_mode = 'list'
            st.session_state.edit_task_id = None
            st.rerun()

# ============================================================================
# DELETE CONFIRMATION MODAL
# ============================================================================

# SOLUTION 12: Delete confirmation
if st.session_state.get('delete_task_id'):
    st.divider()
    st.warning("⚠️ **Delete Confirmation**")

    try:
        task = api.get_task(st.session_state.delete_task_id)

        st.write(f"Are you sure you want to delete task: **{task['title']}**?")
        st.caption("This action cannot be undone.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm Delete", type="primary"):
                try:
                    api.delete_task(st.session_state.delete_task_id)
                    st.success("✅ Task deleted successfully!")
                    st.session_state.delete_task_id = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting task: {e}")

        with col2:
            if st.button("❌ Cancel"):
                st.session_state.delete_task_id = None
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error loading task: {e}")
        st.session_state.delete_task_id = None

# ============================================================================
# STATISTICS
# ============================================================================

st.divider()
st.subheader("📊 Statistics")

# SOLUTION 13: Display statistics
try:
    response = api.get_tasks()
    all_tasks = response['articles']
    my_tasks = [t for t in all_tasks if t['author']['id'] == st.session_state.user['id']]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tasks", len(my_tasks))

    with col2:
        completed = sum(1 for t in my_tasks if t['published'])
        st.metric("Completed", completed)

    with col3:
        pending = sum(1 for t in my_tasks if not t['published'])
        st.metric("Pending", pending)

except Exception as e:
    st.caption("Could not load statistics")

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
    - [x] Can create new task
    - [x] Validation works (required fields)
    - [x] Success message appears
    - [x] Redirects to list view
    - [x] New task appears in list

    **Read:**
    - [x] All tasks display correctly
    - [x] Task details are accurate
    - [x] Status shows correctly
    - [x] Loading spinner appears

    **Update:**
    - [x] Can click edit on a task
    - [x] Form pre-fills with current data
    - [x] Can modify fields
    - [x] Changes save correctly
    - [x] Updated data shows in list

    **Delete:**
    - [x] Can click delete on a task
    - [x] Confirmation appears
    - [x] Can confirm delete
    - [x] Can cancel delete
    - [x] Task removed from list

    **Error Handling:**
    - [x] Errors show user-friendly messages
    - [x] App doesn't crash on errors
    - [x] Invalid data rejected
    """)
