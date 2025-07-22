import streamlit as st
from components.interview_prep_form import show_interview_prep_form
from components.result_display import display_interview_prep_results
from components.sidebar import render_sidebar

# Ask for name in the sidebar
user_id = render_sidebar()

st.header("Interview Q&A Preparation")

if not user_id:
    st.warning("Please enter your **name** in the sidebar.")
else:
    interview_prep_session_id = show_interview_prep_form(user_id)
    if interview_prep_session_id:
        display_interview_prep_results(interview_prep_session_id)
