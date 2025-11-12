"""
Demo 1: Streamlit Basics
Chapter 6: Frontend Development with Streamlit

This demo showcases all the fundamental Streamlit components and features.
Use this as a reference for building Streamlit applications.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, time
import time as time_module

# ============================================================================
# PAGE CONFIGURATION (must be first Streamlit command)
# ============================================================================

st.set_page_config(
    page_title="Streamlit Basics Demo",
    page_icon="🎈",
    layout="wide",  # or "centered"
    initial_sidebar_state="expanded"
)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'counter' not in st.session_state:
        st.session_state.counter = 0

    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

    if 'submitted_form' not in st.session_state:
        st.session_state.submitted_form = False

init_session_state()

# ============================================================================
# TITLE & INTRODUCTION
# ============================================================================

st.title("🎈 Streamlit Basics Demo")
st.markdown("""
Welcome to the Streamlit Basics Demo! This application demonstrates all the fundamental
Streamlit components you'll need to build interactive web applications.

**Navigation:** Use the tabs below to explore different component categories.
""")

st.divider()

# ============================================================================
# TABS FOR ORGANIZATION
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Text & Display",
    "🎮 Input Widgets",
    "📊 Data Display",
    "🎨 Layout",
    "💾 Session State",
    "📁 File Upload"
])

# ============================================================================
# TAB 1: TEXT & DISPLAY
# ============================================================================

with tab1:
    st.header("Text & Display Components")

    # Text elements
    st.subheader("1. Text Elements")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Code:**")
        st.code("""
st.title("Title")
st.header("Header")
st.subheader("Subheader")
st.text("Fixed width text")
st.markdown("**Bold** and *italic*")
st.write("Magic write!")
        """, language="python")

    with col2:
        st.write("**Output:**")
        st.title("Title")
        st.header("Header")
        st.subheader("Subheader")
        st.text("Fixed width text")
        st.markdown("**Bold** and *italic*")
        st.write("Magic write!")

    st.divider()

    # Status messages
    st.subheader("2. Status Messages")

    col1, col2 = st.columns(2)

    with col1:
        st.code("""
st.success("Success!")
st.info("Info message")
st.warning("Warning!")
st.error("Error message")
        """, language="python")

    with col2:
        st.success("✅ Success!")
        st.info("ℹ️ Info message")
        st.warning("⚠️ Warning!")
        st.error("❌ Error message")

    st.divider()

    # Containers
    st.subheader("3. Containers & Expandable Sections")

    with st.expander("Click to expand/collapse"):
        st.write("This content is hidden until expanded!")
        st.write("You can put any Streamlit components here.")

    # Empty container example
    placeholder = st.empty()
    placeholder.write("This is a placeholder that can be updated...")

    if st.button("Update Placeholder"):
        placeholder.success("Placeholder updated!")

# ============================================================================
# TAB 2: INPUT WIDGETS
# ============================================================================

with tab2:
    st.header("Input Widgets")

    st.subheader("1. Text Input")

    col1, col2 = st.columns(2)

    with col1:
        text_input = st.text_input("Enter your name:", placeholder="John Doe")
        st.write(f"Hello, {text_input}!" if text_input else "Please enter your name")

        password = st.text_input("Password:", type="password")
        if password:
            st.write("Password entered (hidden)")

        text_area = st.text_area("Your message:", height=100)
        st.write(f"Character count: {len(text_area)}")

    with col2:
        st.code("""
text_input = st.text_input("Enter name:")
password = st.text_input("Password:", type="password")
text_area = st.text_area("Message:")
        """, language="python")

    st.divider()

    st.subheader("2. Number Input")

    col1, col2 = st.columns(2)

    with col1:
        number = st.number_input("Enter a number:", min_value=0, max_value=100, value=25, step=1)
        st.write(f"You entered: {number}")

        slider = st.slider("Select a range:", 0, 100, (25, 75))
        st.write(f"Selected range: {slider[0]} to {slider[1]}")

        rating = st.slider("Rate this demo:", 1, 5, 3)
        st.write("⭐" * rating)

    with col2:
        st.code("""
number = st.number_input("Number:", 0, 100)
slider = st.slider("Range:", 0, 100, (25, 75))
rating = st.slider("Rating:", 1, 5, 3)
        """, language="python")

    st.divider()

    st.subheader("3. Selection Widgets")

    col1, col2 = st.columns(2)

    with col1:
        select_box = st.selectbox(
            "Choose a category:",
            ["Technology", "Science", "Business", "Health", "Sports"]
        )
        st.write(f"Selected: {select_box}")

        multi_select = st.multiselect(
            "Select tags:",
            ["python", "flask", "streamlit", "api", "tutorial", "beginners"],
            default=["python", "streamlit"]
        )
        st.write(f"Selected tags: {', '.join(multi_select)}")

        checkbox = st.checkbox("I agree to the terms", value=False)
        st.write(f"Agreed: {checkbox}")

        radio = st.radio("Choose status:", ["Draft", "Published", "Archived"])
        st.write(f"Status: {radio}")

    with col2:
        st.code("""
selectbox = st.selectbox("Category:", options)
multiselect = st.multiselect("Tags:", options)
checkbox = st.checkbox("Agree", False)
radio = st.radio("Status:", options)
        """, language="python")

    st.divider()

    st.subheader("4. Date & Time Input")

    col1, col2 = st.columns(2)

    with col1:
        date_input = st.date_input("Select a date:", value=date.today())
        st.write(f"Selected date: {date_input}")

        time_input = st.time_input("Select a time:", value=time(9, 0))
        st.write(f"Selected time: {time_input}")

    with col2:
        st.code("""
date_input = st.date_input("Date:")
time_input = st.time_input("Time:")
        """, language="python")

    st.divider()

    st.subheader("5. Buttons")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Regular Button"):
            st.success("Button clicked!")

    with col2:
        if st.button("Primary Button", type="primary"):
            st.success("Primary clicked!")

    with col3:
        if st.button("Download Button", type="secondary"):
            st.success("Download clicked!")

# ============================================================================
# TAB 3: DATA DISPLAY
# ============================================================================

with tab3:
    st.header("Data Display")

    st.subheader("1. DataFrames & Tables")

    # Sample data
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'City': ['New York', 'London', 'Paris', 'Tokyo', 'Sydney'],
        'Score': [92, 87, 95, 88, 91]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Interactive DataFrame:**")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.write("**Static Table:**")
        st.table(df)

    st.divider()

    st.subheader("2. Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Users",
            value=1234,
            delta=12,
            delta_color="normal"
        )

    with col2:
        st.metric(
            label="Revenue",
            value="$45.2K",
            delta="+15%"
        )

    with col3:
        st.metric(
            label="Page Views",
            value=8432,
            delta=-234,
            delta_color="inverse"
        )

    with col4:
        st.metric(
            label="Conversion",
            value="4.2%",
            delta="0.8%"
        )

    st.divider()

    st.subheader("3. Charts")

    # Line chart
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Series A', 'Series B', 'Series C']
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Line Chart:**")
        st.line_chart(chart_data)

    with col2:
        st.write("**Area Chart:**")
        st.area_chart(chart_data)

    # Bar chart
    st.write("**Bar Chart:**")
    st.bar_chart(chart_data)

    st.divider()

    st.subheader("4. JSON Display")

    sample_json = {
        'user': {
            'id': 1,
            'username': 'johndoe',
            'email': 'john@example.com',
            'active': True
        },
        'articles': [
            {'id': 1, 'title': 'First Article'},
            {'id': 2, 'title': 'Second Article'}
        ]
    }

    st.json(sample_json)

# ============================================================================
# TAB 4: LAYOUT
# ============================================================================

with tab4:
    st.header("Layout Components")

    st.subheader("1. Columns")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Column 1")
        st.write("This is the first column")

    with col2:
        st.success("Column 2")
        st.write("This is the second column")

    with col3:
        st.warning("Column 3")
        st.write("This is the third column")

    st.divider()

    st.subheader("2. Columns with Different Widths")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.info("Wider column (2/3)")
        st.write("This column takes 2/3 of the width")

    with col2:
        st.success("Narrower column (1/3)")
        st.write("This column takes 1/3")

    st.divider()

    st.subheader("3. Container")

    with st.container():
        st.write("This is inside a container")
        st.button("Container Button")

    st.write("This is outside the container")

    st.divider()

    st.subheader("4. Sidebar")

    st.write("Check the sidebar on the left for interactive elements!")

# ============================================================================
# TAB 5: SESSION STATE
# ============================================================================

with tab5:
    st.header("Session State Management")

    st.markdown("""
    **Session State** allows you to persist data across reruns.
    Without session state, variables reset on every interaction!
    """)

    st.subheader("1. Counter Example")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("➕ Increment"):
            st.session_state.counter += 1

    with col2:
        if st.button("➖ Decrement"):
            st.session_state.counter -= 1

    with col3:
        if st.button("🔄 Reset"):
            st.session_state.counter = 0

    st.metric("Current Count", st.session_state.counter)

    st.divider()

    st.subheader("2. Form Data Persistence")

    # Store form data in session state
    name = st.text_input(
        "Name:",
        value=st.session_state.user_data.get('name', ''),
        key='name_input'
    )

    email = st.text_input(
        "Email:",
        value=st.session_state.user_data.get('email', ''),
        key='email_input'
    )

    if st.button("Save Data"):
        st.session_state.user_data = {
            'name': name,
            'email': email,
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        st.success("Data saved to session state!")

    if st.session_state.user_data:
        st.write("**Stored Data:**")
        st.json(st.session_state.user_data)

    st.divider()

    st.subheader("3. Complete Session State")

    with st.expander("View all session state"):
        st.write(st.session_state)

# ============================================================================
# TAB 6: FILE UPLOAD
# ============================================================================

with tab6:
    st.header("File Upload")

    st.subheader("1. Single File Upload")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'csv', 'json', 'jpg', 'png'],
        help="Supported formats: txt, csv, json, jpg, png"
    )

    if uploaded_file:
        # File details
        st.success(f"File uploaded: {uploaded_file.name}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("File Name", uploaded_file.name)

        with col2:
            file_size = uploaded_file.size / 1024  # KB
            st.metric("Size", f"{file_size:.2f} KB")

        with col3:
            st.metric("Type", uploaded_file.type)

        # Show file content based on type
        if uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode()
            st.text_area("File Content:", content, height=200)

        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)

        elif uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    st.divider()

    st.subheader("2. Multiple File Upload")

    uploaded_files = st.file_uploader(
        "Choose multiple files",
        accept_multiple_files=True,
        type=['jpg', 'png', 'gif']
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded")

        # Display images in columns
        cols = st.columns(min(len(uploaded_files), 3))

        for idx, file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(file, caption=file.name, use_column_width=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("⚙️ Sidebar")

    st.write("This is the sidebar - perfect for filters and settings!")

    st.divider()

    st.subheader("Filters")

    sidebar_category = st.selectbox(
        "Category:",
        ["All", "Technology", "Science", "Business"]
    )

    sidebar_published = st.checkbox("Published only", value=True)

    sidebar_date_range = st.date_input(
        "Date range:",
        value=(date.today(), date.today())
    )

    if st.button("Apply Filters", type="primary"):
        st.success("Filters applied!")

    st.divider()

    st.subheader("About")
    st.info("""
    This is a demonstration of Streamlit's core components.

    **Features:**
    - Text & display
    - Input widgets
    - Data visualization
    - Layout options
    - Session state
    - File uploads
    """)

# ============================================================================
# FORMS
# ============================================================================

st.divider()

st.header("📋 Forms")

st.markdown("""
Forms allow you to batch multiple inputs together. The inputs inside a form
won't trigger a rerun until the submit button is clicked.
""")

with st.form("demo_form"):
    st.subheader("Contact Form")

    form_name = st.text_input("Name:")
    form_email = st.text_input("Email:")
    form_message = st.text_area("Message:", height=100)

    col1, col2 = st.columns(2)

    with col1:
        form_category = st.selectbox("Category:", ["General", "Support", "Feedback"])

    with col2:
        form_priority = st.radio("Priority:", ["Low", "Medium", "High"])

    submitted = st.form_submit_button("Submit", type="primary")

    if submitted:
        if not form_name or not form_email or not form_message:
            st.error("Please fill all required fields!")
        else:
            st.success("Form submitted successfully!")
            st.balloons()

            # Show submitted data
            with st.expander("Submitted Data"):
                st.json({
                    'name': form_name,
                    'email': form_email,
                    'message': form_message,
                    'category': form_category,
                    'priority': form_priority,
                    'submitted_at': datetime.now().isoformat()
                })

# ============================================================================
# PROGRESS & STATUS
# ============================================================================

st.divider()

st.header("⏳ Progress & Status")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Progress Bar")

    progress_bar = st.progress(0)
    status_text = st.empty()

    if st.button("Run Progress"):
        for i in range(101):
            progress_bar.progress(i)
            status_text.text(f"Progress: {i}%")
            time_module.sleep(0.02)

        status_text.success("Complete!")

with col2:
    st.subheader("Spinner")

    if st.button("Show Spinner"):
        with st.spinner("Loading..."):
            time_module.sleep(2)
        st.success("Done!")

# ============================================================================
# SPECIAL EFFECTS
# ============================================================================

st.divider()

st.header("🎉 Special Effects")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎈 Balloons"):
        st.balloons()

with col2:
    if st.button("❄️ Snow"):
        st.snow()

with col3:
    if st.button("🎊 Success"):
        st.success("Hooray!")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("""
---
**Streamlit Basics Demo** | Chapter 6: Frontend Development with Streamlit

Learn more: [Streamlit Documentation](https://docs.streamlit.io/) | [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
""")
