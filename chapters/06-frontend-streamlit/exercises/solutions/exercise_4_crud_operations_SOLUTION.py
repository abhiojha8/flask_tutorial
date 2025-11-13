"""
Exercise 4: CRUD Operations 🟡 - SOLUTION
Difficulty: Intermediate
Estimated Time: 60 minutes

Complete solution with all TODOs implemented.

DEMO CREDENTIALS:
Email: john@example.com
Password: Password123!
"""

import streamlit as st
import requests
from typing import Dict, Optional

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

    # TODO 1: SOLUTION
    if 'edit_task_id' not in st.session_state:
        st.session_state.edit_task_id = None
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'list'
    if 'delete_task_id' not in st.session_state:
        st.session_state.delete_task_id = None

def is_authenticated() -> bool:
    return st.session_state.token is not None and st.session_state.user is not None

def require_auth():
    if not is_authenticated():
        st.warning("⚠️ You must be logged in to use this app.")
        st.info("Please login below:")

        with st.form("quick_login"):
            email = st.text_input("Email", value="john@example.com")
            password = st.text_input("Password", type="password", value="Password123!")
            submit = st.form_submit_button("Login")

            if submit:
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
# API CLIENT
# ============================================================================

class TaskAPIClient:
    def __init__(self, token: str):
        self.base_url = API_BASE_URL
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    # TODO 2: SOLUTION
    def get_tasks(self) -> Dict:
        response = requests.get(f"{self.base_url}/articles", headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    # TODO 3: SOLUTION
    def get_task(self, task_id: int) -> Dict:
        response = requests.get(f"{self.base_url}/articles/{task_id}", headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    # TODO 4: SOLUTION
    def create_task(self, task_data: Dict) -> Dict:
        response = requests.post(
            f"{self.base_url}/articles",
            json=task_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    # TODO 5: SOLUTION
    def update_task(self, task_id: int, task_data: Dict) -> Dict:
        response = requests.put(
            f"{self.base_url}/articles/{task_id}",
            json=task_data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    # TODO 6: SOLUTION
    def delete_task(self, task_id: int) -> Dict:
        response = requests.delete(
            f"{self.base_url}/articles/{task_id}",
            headers=self._get_headers()
        )
        if response.status_code == 204:
            return {'message': 'Deleted'}
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

init_session_state()
require_auth()

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

    # TODO 7: SOLUTION
    if st.button("📋 View All Tasks", use_container_width=True):
        st.session_state.view_mode = 'list'
        st.rerun()

    if st.button("➕ Create New Task", use_container_width=True, type="primary"):
        st.session_state.view_mode = 'create'
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

# TODO 8: SOLUTION
view_mode = st.session_state.get('view_mode', 'list')

# ============================================================================
# VIEW: LIST ALL TASKS
# ============================================================================

if view_mode == 'list':
    st.header("📋 All Tasks")

    # TODO 9: SOLUTION
    try:
        with st.spinner("Loading tasks..."):
            response = api.get_tasks()
            tasks = response.get('articles', [])

        if tasks:
            for task in tasks:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.subheader(f"📄 {task['title']}")
                        status = "✅ Completed" if task['published'] else "📝 Pending"
                        st.caption(f"{status} | {task['views']} views")

                        content_preview = task['content'][:150]
                        if len(task['content']) > 150:
                            content_preview += "..."
                        st.write(content_preview)

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
            st.info("📭 No tasks found. Create your first task!")

    except Exception as e:
        st.error(f"❌ Error loading tasks: {e}")

# ============================================================================
# VIEW: CREATE TASK
# ============================================================================

elif view_mode == 'create':
    st.header("➕ Create New Task")

    # TODO 10: SOLUTION
    with st.form("create_task_form"):
        title = st.text_input("Task Title", max_chars=200, placeholder="Enter task title...")
        description = st.text_area("Description", height=150, placeholder="Enter task description...")
        completed = st.checkbox("Mark as completed")

        col1, col2 = st.columns(2)

        with col1:
            submit = st.form_submit_button("✅ Create Task", type="primary", use_container_width=True)

        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

        if submit:
            if not title or not description:
                st.error("❌ Title and description are required")
            elif len(description) < 10:
                st.error("❌ Description must be at least 10 characters")
            else:
                try:
                    task_data = {
                        'title': title,
                        'content': description,
                        'published': completed
                    }

                    with st.spinner("Creating task..."):
                        result = api.create_task(task_data)

                    st.success(f"✅ Task created: {result['title']}")
                    st.session_state.view_mode = 'list'
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error creating task: {e}")

        if cancel:
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
        # TODO 11: SOLUTION
        try:
            with st.spinner(f"Loading task {task_id}..."):
                task = api.get_task(task_id)

            st.info(f"Editing: {task['title']}")

            with st.form("edit_task_form"):
                title = st.text_input("Task Title", value=task['title'], max_chars=200)
                description = st.text_area("Description", value=task['content'], height=150)
                completed = st.checkbox("Mark as completed", value=task['published'])

                col1, col2 = st.columns(2)

                with col1:
                    submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

                with col2:
                    cancel = st.form_submit_button("❌ Cancel", use_container_width=True)

                if submit:
                    if not title or not description:
                        st.error("❌ Title and description are required")
                    elif len(description) < 10:
                        st.error("❌ Description must be at least 10 characters")
                    else:
                        try:
                            task_data = {
                                'title': title,
                                'content': description,
                                'published': completed
                            }

                            with st.spinner("Saving changes..."):
                                result = api.update_task(task_id, task_data)

                            st.success(f"✅ Task updated: {result['title']}")
                            st.session_state.view_mode = 'list'
                            st.session_state.edit_task_id = None
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error updating task: {e}")

                if cancel:
                    st.session_state.view_mode = 'list'
                    st.session_state.edit_task_id = None
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Error loading task: {e}")

# ============================================================================
# DELETE CONFIRMATION MODAL
# ============================================================================

# TODO 12: SOLUTION
if st.session_state.get('delete_task_id'):
    st.divider()
    st.warning("⚠️ Confirm Deletion")

    try:
        task_id = st.session_state.delete_task_id
        task = api.get_task(task_id)

        st.write(f"**Task:** {task['title']}")
        st.caption(f"ID: {task_id}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
                try:
                    api.delete_task(task_id)
                    st.success("✅ Task deleted!")
                    st.session_state.delete_task_id = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting task: {e}")

        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.delete_task_id = None
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.session_state.delete_task_id = None

# ============================================================================
# STATISTICS
# ============================================================================

st.divider()
st.subheader("📊 Statistics")

# TODO 13: SOLUTION
try:
    with st.spinner("Loading statistics..."):
        response = api.get_tasks()
        tasks = response.get('articles', [])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tasks", len(tasks))

    with col2:
        completed = len([t for t in tasks if t['published']])
        st.metric("Completed", completed)

    with col3:
        pending = len([t for t in tasks if not t['published']])
        st.metric("Pending", pending)

except Exception as e:
    st.error(f"❌ Error loading statistics: {e}")

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
