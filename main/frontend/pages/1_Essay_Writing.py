import streamlit as st
from components.sidebar import render_sidebar
from components.essay_form import show_essay_form
from components.result_display import display_essay_results

# Sidebar selection
feature, user_id = render_sidebar()

st.title("📝 Essay Writing Assistant")

if feature != "Essay Writing":
    st.warning("Please select **Essay Writing** in the sidebar.")
else:
    session_id = show_essay_form(user_id)
    if session_id:
        display_essay_results(session_id)
