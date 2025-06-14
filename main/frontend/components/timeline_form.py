import streamlit as st
from utils.api import create_timeline_planner_session


    
def show_timeline_form(user_id: str):
    # University names and level of study
    col1, col2 = st.columns(2)
    with col1:
        universities_input = st.text_input(
            "University Names (comma-separated)", 
            placeholder="E.g., University of Oxford, Harvard University, UNSW", 
            help="Enter the full names of one or more universities, separated by commas"
        )

    with col2:
        level = st.selectbox(
            "Level of Study", 
            options=["Select Level of Study", "Undergraduate", "Postgraduate", "PhD", "Diploma", "Other"], 
            help="Select the level of study you are applying for"
        )

    # Applicant type and nationality
    col3, col4 = st.columns(2)
    with col3:
        applicant_type = st.selectbox(
            "Applicant Type", 
            options=["Select Applicant Type", "Domestic", "International"], 
            help="Choose if you're applying as a domestic or international student"
        )

    nationality = ""
    with col4:
        if applicant_type == "International":
            nationality = st.text_input(
                "Nationality", 
                placeholder="Enter your nationality", 
                help="Required for international applicants"
            )

    intake = st.text_input(
        "Preferred university intake period",
        placeholder="e.g., September 2025",
        help="Enter the month and year you prefer to begin your university studies."
    )

    # Timeline preference input
    applicant_availability = st.text_area(
        "Application Timeline Preferences (Optional)", 
        placeholder="E.g. Prefer essay deadlines in October; unavailable for interviews on weekends; need scholarships finalized by December.", 
        help=(
            "Add any preferences or constraints that could affect your application timeline. "
            "This may include preferred months for tasks like essay writing, unavailable dates, or scholarship deadlines."
        )
    )

    # Submit and validation
    if st.button("Start Application Timeline Planner"):
        # Convert comma-separated string to a list
        university_list = [u.strip() for u in universities_input.split(",") if u.strip()]
        
        if (
            not university_list
            or level == "Select Level of Study" 
            or not intake
            or applicant_type == "Select Applicant Type" 
            or (applicant_type == "International" and not nationality)
        ):
            st.error("Please fill in all required fields before proceeding.")
            return None
        
        session_id = create_timeline_planner_session(
            user_id=user_id,
            universities=university_list,
            level=level,
            applicant_type=applicant_type,
            nationality=nationality if nationality else "none",
            intake=intake,
            applicant_availability=applicant_availability if applicant_availability else "none"
        )
        st.success(f"Timeline Planner session started: **{session_id}**")
        return session_id

    return None
