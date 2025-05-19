import streamlit as st
from utils.api import (
    get_essay_status,
    get_essay_result,
    get_program_analysis_status,
    get_program_analysis_result,
)

def display_essay_results(session_id: str):
    """Poll and display results for an essay-writing session."""
    st.subheader("Essay Writing Results")
    status = get_essay_status(session_id)
    st.write("Status:", status["status"].capitalize())

    if status["status"] == "completed":
        res = get_essay_result(session_id)
        st.markdown("### Structured Outline")
        st.json(res["outline"])
        st.markdown("### Refined Essay")
        st.text_area("Refined Draft", res["refined_draft"], height=300)

def display_program_analysis_results(session_id: str):
    """Poll and display results for a program-analysis session."""
    st.subheader("Program Analysis Results")
    status = get_program_analysis_status(session_id)
    st.write("Status:", status["status"].capitalize())

    if status["status"] == "completed":
        res = get_program_analysis_result(session_id)
        st.markdown("#### Raw Admissions Data")
        st.json(res["raw_admissions_data"])
        st.markdown("#### Structured Admissions Data")
        st.json(res["structured_admissions_data"])
        st.markdown("#### Comparison Report")
        st.json(res["program_comparison_report"])
