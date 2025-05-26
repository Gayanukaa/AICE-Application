import streamlit as st
from components.analysis_form import show_analysis_form
from components.result_display import display_program_analysis_results
from components.sidebar import render_sidebar

# Ask for User ID in the sidebar
user_id = render_sidebar()

st.header("📊 Program Analysis")

if not user_id:
    st.warning("Please enter your **User ID** in the sidebar.")
else:
    session_id = show_analysis_form(user_id)
    if session_id:
        display_program_analysis_results(session_id)
