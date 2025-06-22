import streamlit as st
from components.result_display import display_timeline_planner_results
from components.sidebar import render_sidebar
from components.timeline_form import show_timeline_form

# Ask for User ID in the sidebar
user_id = render_sidebar()

st.header("Application Timeline planner")

if not user_id:
    st.warning("Please enter your **User ID** in the sidebar.")
else:
    session_id = show_timeline_form(user_id)
    if session_id:
        display_timeline_planner_results(session_id)
