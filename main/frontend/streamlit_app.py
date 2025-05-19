import streamlit as st

from components.sidebar import render_sidebar
from components.essay_form import show_essay_form
from components.analysis_form import show_analysis_form
from components.result_display import (
    display_essay_results,
    display_program_analysis_results,
)

def main():
    st.set_page_config(page_title="AI College Exploration", layout="wide")
    feature, user_id = render_sidebar()

    if feature == "Essay Writing":
        st.title("📝 Essay Writing Assistant")
        session_id = show_essay_form(user_id)
        if session_id:
            display_essay_results(session_id)

    elif feature == "Program Analysis":
        st.title("📊 Program Analysis")
        session_id = show_analysis_form(user_id)
        if session_id:
            display_program_analysis_results(session_id)

    else:
        st.error("Unknown feature selected.")

if __name__ == "__main__":
    main()
