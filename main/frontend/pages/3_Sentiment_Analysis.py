import streamlit as st
from components.sidebar import render_sidebar
from utils.api import sentiment_analysis

st.header("🕵️ Sentiment + Reddit Insights")
user_id = render_sidebar()

if not user_id:
    st.warning("Please enter your **name** in the sidebar.")
else:
    review = st.text_area(
        "Enter a single student review (we’ll find similar Reddit posts)",
        height=150,
        placeholder="“Professors are great, but campus housing needs work.”",
    )

    if st.button("Analyze & Fetch Reddit"):
        if not review.strip():
            st.error("Please enter a review to analyze.")
        else:
            with st.spinner("Fetching Reddit posts and summarizing…"):
                try:
                    result = sentiment_analysis([review.strip()])
                except Exception as e:
                    st.error(f"Failed: {e}")
                else:
                    st.markdown("### 🔗 Related Reddit Posts")
                    for p in result["reddit_posts"]:
                        st.markdown(f"- [{p['title']}]({p['url']})")

                    st.markdown("---")
                    st.markdown("### ✏️ Summary of Overall Sentiment")
                    st.write(result["summary"])
