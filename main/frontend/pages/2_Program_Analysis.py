import streamlit as st
from components.sidebar import render_sidebar
from components.analysis_form import show_analysis_form
from components.result_display import display_program_analysis_results

# Sidebar selection
feature, user_id = render_sidebar()

st.title("📊 Program Analysis")

if feature != "Program Analysis":
    st.warning("Please select **Program Analysis** in the sidebar.")
else:
    session_id = show_analysis_form(user_id)
    if session_id:
        display_program_analysis_results(session_id)
