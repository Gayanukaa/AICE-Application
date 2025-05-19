import streamlit as st
from utils.api import create_essay_session

def show_essay_form(user_id: str):
    """Display the essay-writing form and return a new session_id (or None)."""
    st.header("Essay Writing Assistant")
    if not user_id:
        st.warning("Please enter your User ID in the sidebar.")
        return None

    essay_text = st.text_area(
        "Paste Your Essay Text",
        height=200,
        help="Enter the draft essay you want to structure and refine."
    )
    target_university = st.text_input(
        "Target University",
        help="Name of the university for which you are applying."
    )
    style_guidelines = st.text_input(
        "Style Guidelines",
        help="Any specific tone or formatting requirements."
    )

    if st.button("Start Essay Session"):
        if not essay_text.strip() or not target_university or not style_guidelines:
            st.error("All fields are required to start an essay session.")
            return None

        session_id = create_essay_session(
            user_id=user_id,
            essay_text=essay_text,
            target_university=target_university,
            style_guidelines=style_guidelines
        )
        st.success(f"Essay session started: **{session_id}**")
        return session_id

    return None
