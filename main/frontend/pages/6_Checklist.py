import streamlit as st
from components.checklist_form import show_checklist_form
from components.result_display import display_checklist_results
from components.sidebar import render_sidebar

# Ask for User ID in the sidebar
user_id = render_sidebar()

st.header("Dynamic Application Checklist Generator")

if not user_id:
    st.warning("Please enter your **User ID** in the sidebar.")
else:
    checklist_session_id = show_checklist_form(user_id)
    if checklist_session_id:
        display_checklist_results(checklist_session_id)
