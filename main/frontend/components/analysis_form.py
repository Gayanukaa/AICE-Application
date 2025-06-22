import streamlit as st
from utils.api import create_program_analysis_session


def show_analysis_form(user_id: str):
    """Display the program-analysis form and return a new session_id (or None)."""
    st.header("Program Analysis")
    if not user_id:
        st.warning("Please enter your name in the sidebar.")
        return None

    uni_input = st.text_area(
        "Universities (comma-separated)",
        help="List the universities you want to compare.",
    )
    criteria_input = st.text_input(
        "Comparison Criteria (comma-separated)",
        help="E.g., cost, ranking, curriculum, scholarships.",
    )

    if st.button("Start Program Analysis"):
        universities = [u.strip() for u in uni_input.split(",") if u.strip()]
        criteria = [c.strip() for c in criteria_input.split(",") if c.strip()]

        if not universities or not criteria:
            st.error("Please provide at least one university and one criterion.")
            return None

        session_id = create_program_analysis_session(
            user_id=user_id, university_list=universities, comparison_criteria=criteria
        )
        st.success(f"Program-analysis session started: **{session_id}**")
        return session_id

    return None
