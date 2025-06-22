import streamlit as st
from utils.api import create_cost_breakdown_session


def show_cost_form(user_id: str):
    col1, col2 = st.columns(2)
    with col1:
        university = st.text_input(
            "Target University",
            help="Enter the name of the university you wish to apply to.",
        )
    with col2:
        course = st.text_input(
            "Course Name",
            placeholder="Course name - program level",
            help="Enter the name of the course and program level.",
        )

    col3, col4 = st.columns(2)
    with col3:
        applicant_type = st.selectbox(
            "Applicant Type", ["Select Applicant type", "Domestic", "International"]
        )
    with col4:
        location = st.text_input(
            "Residential location",
            placeholder="e.g., New York, Melbourne, or Singapore",
            help="Enter your city, state, or country.",
        )

    preferences = st.text_input(
        "Preferences (Optional)",
        placeholder="e.g., I don't need accommodation, I prefer online classes, I will commute by train",
        help="Mention any additional preferences like accommodation needs, study format, or transport plans.",
    )

    if st.button("Start Cost Breakdown"):
        if (
            not university
            or not course
            or not location
            or applicant_type == "Select Applicant type"
        ):
            st.error("All fields except 'Preferences' are required.")
            return None

        session_id = create_cost_breakdown_session(
            user_id=user_id,
            university=university,
            course=course,
            applicant_type=applicant_type,
            location=location,
            preferences=preferences if preferences else None,
        )
        st.success(f"Cost Breakdown session started: **{session_id}**")
        return session_id

    return None
