# Chapter 6 Exercises

Practice building Streamlit applications and integrating with Flask backend.

## Setup

Before starting these exercises, ensure:

1. **Backend is running:**
   ```bash
   cd ../backend
   python app.py
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Exercises Overview

| Exercise | Difficulty | Topic | Estimated Time |
|----------|-----------|-------|----------------|
| Exercise 1 | 🟢 Basic | Streamlit UI Components | 30 minutes |
| Exercise 2 | 🟢 Basic | API Integration | 45 minutes |
| Exercise 3 | 🟡 Intermediate | Authentication Flow | 60 minutes |
| Exercise 4 | 🟡 Intermediate | CRUD Operations | 60 minutes |
| Exercise 5 | 🔴 Advanced | File Upload & Validation | 90 minutes |

## Exercise 1: Streamlit UI Components 🟢

**File:** `exercise_1_ui_components.py`

**Goal:** Build a simple Streamlit app that displays information using various UI components.

**Requirements:**
- Display article data from the API
- Use columns for layout
- Show metrics for statistics
- Add filters and search

**Skills Practiced:**
- Streamlit basic components
- Layout with columns
- Metrics and data display
- User input widgets

**Instructions:**
```bash
streamlit run exercise_1_ui_components.py
```

## Exercise 2: API Integration 🟢

**File:** `exercise_2_api_integration.py`

**Goal:** Create an app that fetches and displays data from the Flask backend API.

**Requirements:**
- Fetch articles from API
- Display in a list
- Handle API errors
- Show loading states

**Skills Practiced:**
- HTTP requests with `requests` library
- Error handling
- Loading spinners
- API response parsing

**Instructions:**
```bash
streamlit run exercise_2_api_integration.py
```

## Exercise 3: Authentication Flow 🟡

**File:** `exercise_3_authentication.py`

**Goal:** Implement user login and registration with session management.

**Requirements:**
- Login form
- Registration form
- Store JWT token in session state
- Show user info when logged in
- Logout functionality

**Skills Practiced:**
- Session state management
- Form validation
- JWT token handling
- Protected routes

**Instructions:**
```bash
streamlit run exercise_3_authentication.py
```

## Exercise 4: CRUD Operations 🟡

**File:** `exercise_4_crud_operations.py`

**Goal:** Build a complete task manager with Create, Read, Update, Delete operations.

**Requirements:**
- View all tasks (articles)
- Create new tasks
- Edit existing tasks
- Delete tasks
- Requires authentication

**Skills Practiced:**
- CRUD operations
- Form handling
- State management
- API calls with authentication

**Instructions:**
```bash
streamlit run exercise_4_crud_operations.py
```

## Exercise 5: File Upload & Validation 🔴

**File:** `exercise_5_file_upload.py`

**Goal:** Create an app that allows image upload with proper validation.

**Requirements:**
- File upload widget
- File size validation
- File type validation
- Image preview
- Upload to backend

**Skills Practiced:**
- File upload handling
- Validation logic
- Multipart requests
- Image processing
- Error handling

**Instructions:**
```bash
streamlit run exercise_5_file_upload.py
```

## Testing Your Solutions

Each exercise includes TODO comments marking where you need to add code. Follow these steps:

1. **Read the requirements** carefully
2. **Look for TODO comments** in the code
3. **Implement the required functionality**
4. **Test your solution** with the backend
5. **Compare with demo apps** for reference

## Common Issues

### Backend Connection Error

**Problem:** "Cannot connect to backend"

**Solution:**
```bash
# Ensure backend is running
cd ../backend
python app.py
```

### Module Not Found

**Problem:** "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Problem:** "Port 8501 is already in use"

**Solution:**
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

### Session State Not Persisting

**Problem:** Data disappears on interaction

**Solution:**
- Initialize session state at the top of your script
- Use `st.session_state['key']` not local variables
- Check for `st.rerun()` calls

## Tips for Success

1. **Start Simple:** Get basic functionality working first
2. **Test Frequently:** Test each TODO before moving to the next
3. **Use Demo Code:** Reference Demo 1 and Demo 2 for examples
4. **Read Docs:** Streamlit documentation is excellent
5. **Handle Errors:** Always wrap API calls in try/except
6. **User Feedback:** Show loading states and error messages

## Learning Objectives

By completing these exercises, you will:

- ✅ Understand Streamlit component system
- ✅ Know how to integrate frontend with backend API
- ✅ Implement authentication flow with JWT
- ✅ Build CRUD operations with forms
- ✅ Handle file uploads and validation
- ✅ Manage application state effectively
- ✅ Create user-friendly error handling
- ✅ Build production-ready full-stack apps

## Next Steps

After completing these exercises:

1. **Review Solutions:** Check the solutions branch
2. **Enhance Features:** Add your own improvements
3. **Build Projects:** Create your own full-stack apps
4. **Deploy:** Learn to deploy Streamlit apps
5. **Explore More:** Try Streamlit Cloud, authentication providers, etc.

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cheat Sheet](https://docs.streamlit.io/library/cheatsheet)
- [Requests Documentation](https://requests.readthedocs.io/)
- [JWT.io](https://jwt.io/) - Learn about JWT tokens
- Demo 1 and Demo 2 in this chapter

---

**Good luck with the exercises!** 🚀

Remember: The goal is to learn and understand. Take your time and experiment!
