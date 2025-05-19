import streamlit as st

def render_sidebar():
    """Render the main sidebar and return the selected feature and user_id."""
    st.sidebar.title("AI College Exploration")
    user_id = st.sidebar.text_input("User ID", help="Enter your user identifier")
    feature = st.sidebar.radio(
        "Select Feature",
        ("Essay Writing", "Program Analysis"),
        help="Choose which AICE feature to run"
    )
    st.sidebar.markdown("---")
    return feature, user_id
