import streamlit as st


def render_sidebar():
    st.sidebar.title("AICE")

    if "user_id" not in st.session_state:
        st.session_state.user_id = ""

    user_id = st.sidebar.text_input("Name", value=st.session_state.user_id, help="Enter your user identifier")

    if user_id:
        st.session_state.user_id = user_id

    st.sidebar.markdown("---")
    return user_id
