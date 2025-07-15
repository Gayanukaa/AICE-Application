import streamlit as st
from utils.api import create_interview_prep_session


def show_interview_prep_form(user_id: str):
    col1, col2 = st.columns(2)

    with col1:
        university_name = st.text_input(
            "Target University",
            placeholder="e.g., UNSW, University of Toronto, NUS",
            help="Enter the university you are interviewing for."
        )

    with col2:
        course_name = st.text_input(
            "Course Name",
            placeholder="e.g., Computer Science, MBA, Mechanical Engineering",
            help="Enter the specific course or program."
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

    if st.button("Start Interview Q&A"):
        if not university_name or not course_name or program_level == "Select Level":
            st.error("All fields are required. Please complete the form.")
            return None

        session_id = create_interview_prep_session(
            user_id=user_id,
            university_name=university_name,
            course_name=course_name,
            program_level=program_level,
        )
        st.success(f"Interview Q&A session started: **{session_id}**")
        return session_id

    return None
