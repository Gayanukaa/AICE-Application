# frontend/pages/intro_page.py
import streamlit as st

st.title("🎓 AI College Exploration (AICE)")

# Brief description
st.markdown(
    """
Welcome to **AICE**, your personal multi-agent guide through the college research and application journey.
Harness the power of AI to streamline essays, gather admissions intel, and compare programs—all from one place.
""",
    unsafe_allow_html=True,
)

# Features
st.markdown("## 🚀 Features", unsafe_allow_html=True)
st.markdown(
        """
    - 📝 **AI-Powered Essay Writing Assistant**
    • Help brainstorm topic ideas and structure your personal statement
    • Provide grammar, tone & clarity improvements
    • Offer real-time feedback aligned with university-specific expectations

    - 🌐 **University Info Retrieval Agent**
    • Gather admissions requirements, deadlines, fees & scholarships
    • Aggregate and normalize data from official sources

    - 📈 **Program Comparison Agent**
    • Compare programs side-by-side on cost, ranking, curriculum & funding
    • Generate clear, actionable comparison reports
    """,
    unsafe_allow_html=True,
)

# Getting started
st.markdown("## 🏁 Getting Started", unsafe_allow_html=True)
st.markdown(
        """
    1. Enter your **User ID** in the sidebar.
    2. Use the **tabs** on the left to navigate:
    - **Essay Writing**
    - **Program Analysis**
    3. Follow on-screen prompts to begin each feature’s flow.
    """,
    unsafe_allow_html=True,
)

# Contributors
st.markdown("## 🤝 Contributors", unsafe_allow_html=True)
st.markdown(
    """
    - Gayanuka
    - Ushari
    - Nidhan
    """,
    unsafe_allow_html=True,
)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>© 2025 AI College Exploration (AICE). All rights reserved.</p>",
    unsafe_allow_html=True,
)
