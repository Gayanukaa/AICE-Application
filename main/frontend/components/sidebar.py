import streamlit as st

def render_sidebar():
    """Render only the User ID prompt."""
    st.sidebar.title("AICE")
    user_id = st.sidebar.text_input("User ID", help="Enter your user identifier")
    st.sidebar.markdown("---")
    return user_id
