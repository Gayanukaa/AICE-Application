import streamlit as st


def main():
    """Main demo app."""
    st.set_page_config(
        page_title="AI College Exploration (AICE)",
        page_icon="🎓",
        layout="wide",
    )

    pg = st.navigation(
        [
            st.Page(
                "pages/0_Home.py",
                title="Home",
                icon="🏠",
                default=True,  # landing page
            ),
            st.Page(
                "pages/1_Essay_Writing.py",
                title="Essay Writing",
                icon="📝",
            ),
            st.Page(
                "pages/2_Program_Analysis.py",
                title="Program Analysis",
                icon="📊",
            ),
            st.Page(
                "pages/3_Sentiment_Analysis.py",
                title="Sentiment Analysis",
                icon="🕵️",
            ),
            st.Page(
                "pages/4_Cost_Analysis.py",
                title="Cost Breakdown",
                icon="💵",
            ),
            st.Page(
                "pages/5_Timeline_Planner.py",
                title="Timeline Planner",
                icon="🗓️",
            ),
            st.Page(
                "pages/6_Checklist.py",
                title="Checklist Generator",
                icon="📋",
            )
        ]
    )
    pg.run()


if __name__ == "__main__":
    main()
