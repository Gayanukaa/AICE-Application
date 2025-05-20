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

    # only get the user_id now
    user_id = render_sidebar()

    st.title("🎓 AI College Exploration")
    st.write("Welcome! Use the tabs below to pick your workflow.")

    # two tabs: Essay Writing and Program Analysis
    tab_essay, tab_program = st.tabs(["📝 Essay Writing", "📊 Program Analysis"])

    with tab_essay:
        st.header("Essay Writing Assistant")
        if not user_id:
            st.warning("Please enter your **User ID** in the sidebar.")
        else:
            session_id = show_essay_form(user_id)
            if session_id:
                display_essay_results(session_id)

    with tab_program:
        st.header("Program Analysis")
        if not user_id:
            st.warning("Please enter your **User ID** in the sidebar.")
        else:
            session_id = show_analysis_form(user_id)
            if session_id:
                display_program_analysis_results(session_id)

if __name__ == "__main__":
    main()
