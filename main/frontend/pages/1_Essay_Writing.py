import streamlit as st
from components.sidebar import render_sidebar
from components.essay_form import show_essay_form
from components.result_display import display_essay_results

# Ask for User ID in the sidebar
user_id = render_sidebar()

st.header("📝 Essay Writing Assistant")

if not user_id:
    st.warning("Please enter your **User ID** in the sidebar.")
else:
    session_id = show_essay_form(user_id)
    if session_id:
        display_essay_results(session_id)
