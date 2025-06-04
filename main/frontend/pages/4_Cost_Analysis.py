import streamlit as st
from components.cost_form import show_cost_form
from components.result_display import  display_cost_breakdown_results
from components.sidebar import render_sidebar


st.header("💵Cost Breakdown")
user_id = render_sidebar()


if not user_id:
    st.warning("Please enter your **User ID** in the sidebar.")
else:
    session_id = show_cost_form(user_id)
    
    if session_id or "breakdown" in st.session_state:
        display_cost_breakdown_results(session_id)
