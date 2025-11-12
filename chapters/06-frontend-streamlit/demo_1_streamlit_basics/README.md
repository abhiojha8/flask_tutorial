# Demo 1: Streamlit Basics

A comprehensive demonstration of all fundamental Streamlit components and features.

## What's Included

This demo covers:

### 📝 Text & Display
- Titles, headers, subheaders
- Text, markdown, code blocks
- Status messages (success, info, warning, error)
- Containers and expandable sections

### 🎮 Input Widgets
- Text input (regular and password)
- Number input and sliders
- Selection widgets (selectbox, multiselect, checkbox, radio)
- Date and time pickers
- Buttons (regular, primary, secondary)

### 📊 Data Display
- Interactive dataframes
- Static tables
- Metrics with deltas
- Charts (line, area, bar)
- JSON display

### 🎨 Layout
- Columns (equal and custom widths)
- Containers
- Sidebar
- Tabs for organization

### 💾 Session State
- Counter example
- Form data persistence
- Session state inspection

### 📁 File Upload
- Single file upload
- Multiple file upload
- File type handling (text, CSV, images)

### 📋 Forms
- Batched inputs
- Form submission
- Validation

### ⏳ Progress & Status
- Progress bars
- Spinners
- Special effects (balloons, snow)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

1. **Navigate** using the tabs at the top
2. **Interact** with all the widgets and components
3. **Experiment** with the session state examples
4. **Upload** files to see how file handling works
5. **Submit** the form to see validation
6. **Try** the progress bars and special effects

## Learning Tips

- **Play with the widgets** - Change values and see immediate updates
- **Check the sidebar** - See how sidebar components work
- **View session state** - Understand how data persists across reruns
- **Try uploading files** - Upload different file types to see handling
- **Submit the form** - See how form validation works

## Key Concepts Demonstrated

### 1. Script Rerun Behavior
Every interaction triggers a complete script rerun. Watch how:
- Regular variables reset on each rerun
- Session state persists across reruns

### 2. Widget Keys
Some widgets use `key` parameter to connect to session state:
```python
st.text_input("Name:", key='name_input')
```

### 3. Layout Options
See how columns and containers organize content:
```python
col1, col2 = st.columns(2)
with col1:
    st.write("Left column")
```

### 4. Forms
Forms batch inputs to prevent reruns until submission:
```python
with st.form("my_form"):
    name = st.text_input("Name:")
    submitted = st.form_submit_button("Submit")
```

### 5. File Upload
Handle different file types:
- Text files → Display content
- CSV files → Show as dataframe
- Images → Display with `st.image()`

## Code Structure

```python
# Page config (must be first!)
st.set_page_config(...)

# Initialize session state
def init_session_state():
    if 'var' not in st.session_state:
        st.session_state.var = value

# Main content
st.title("App Title")

# Use tabs for organization
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

with tab1:
    # Tab 1 content
    pass

# Sidebar
with st.sidebar:
    # Sidebar content
    pass
```

## Common Patterns

### Pattern 1: Counter
```python
if 'count' not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1
```

### Pattern 2: Form with Validation
```python
with st.form("form"):
    name = st.text_input("Name:")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not name:
            st.error("Name required!")
        else:
            st.success("Submitted!")
```

### Pattern 3: File Upload
```python
file = st.file_uploader("Choose file", type=['csv'])

if file:
    df = pd.read_csv(file)
    st.dataframe(df)
```

### Pattern 4: Columns
```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Metric 1", 100)

with col2:
    st.metric("Metric 2", 200)

with col3:
    st.metric("Metric 3", 300)
```

## Customization

Try modifying:
- Page title and icon in `st.set_page_config()`
- Color scheme (Streamlit uses your system theme)
- Layout from "wide" to "centered"
- Add your own tabs with custom content
- Create your own widgets and forms

## Next Steps

After exploring this demo:
1. Try modifying the components
2. Add your own custom features
3. Experiment with different layouts
4. Move on to **Demo 2** to see Streamlit integrated with Flask backend
5. Complete the exercises to practice building Streamlit apps

## Troubleshooting

**"Module not found"**
- Run `pip install -r requirements.txt`

**"Page not loading"**
- Make sure you're using `streamlit run app.py`
- Check that port 8501 is available

**"Session state not persisting"**
- Make sure you're using `st.session_state['key']` correctly
- Remember to initialize session state at the top of your script

**"Form not submitting"**
- Forms require `st.form_submit_button()` inside the form
- Regular `st.button()` won't work inside forms

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit Community](https://discuss.streamlit.io/)

---

**Enjoy exploring Streamlit!** 🎈

This demo is a complete reference for all basic Streamlit components. Use it as a cheat sheet when building your own apps!
