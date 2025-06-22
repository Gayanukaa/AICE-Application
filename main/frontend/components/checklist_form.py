import streamlit as st
from utils.api import create_checklist_session


def show_checklist_form(user_id: str):
    col1, col2 = st.columns(2)
    with col1:
        universities_input = st.text_input(
            "Target Universities",
            placeholder="e.g., UNSW, University of Toronto, NUS",
            help="Enter one or more universities separated by commas.",
        )
    with col2:
        nationality = st.text_input(
            "Your Nationality",
            placeholder="e.g., Sri Lankan, Indian, American",
            help="Used to customize your checklist based on visa and regional needs.",
        )

    program_level = st.selectbox(
        "Program Level",
        [
            "Select Level",
            "Undergraduate",
            "Postgraduate",
            "PhD",
            "Diploma",
            "Certificate",
        ],
    )

    if st.button("Generate Checklist"):
        if not universities_input or not nationality or program_level == "Select Level":
            st.error("All fields are required.")
            return None

        universities = [u.strip() for u in universities_input.split(",") if u.strip()]

        if not universities:
            st.error("Please enter at least one valid university.")
            return None

        session_id = create_checklist_session(
            user_id=user_id,
            nationality=nationality,
            program_level=program_level,
            universities=universities,
        )
        st.success(f"Checklist session started: **{session_id}**")
        return session_id

    return None
