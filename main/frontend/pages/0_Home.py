import os
from datetime import datetime

import streamlit as st

# --- Timeline data ---
timeline = [
    {"date": "2025-05-01", "event": "Project Kickoff"},
    {"date": "2025-05-10", "event": "Frontend Initiation"},
    {"date": "2025-05-20", "event": "Agent Integration"},
    {"date": "2025-05-30", "event": "Backend MVP Complete"},
    {"date": "2025-06-01", "event": "Beta Release"},
    {"date": None, "event": "Production Launch (Upcoming)"},
]

today = datetime.today().strftime("%Y-%m-%d")

# --- Team data ---
team_members = [
    {
        "name": "Gayanuka Amarasuriya",
        "role": "AI/ML Engineer Intern",
        "github": "https://github.com/Gayanukaa",
        "image_url": "https://via.placeholder.com/150",
    },
    {
        "name": "Ushari Ranasinghe",
        "role": "AI/ML Engineer Intern",
        "github": "https://github.com/ushariRanasinghe",
        "image_url": "https://via.placeholder.com/150",
    },
    {
        "name": "Nidhan Samarasinghe",
        "role": "AI/ML Engineer Intern",
        "github": "https://github.com/Nidhan03",
        "image_url": "https://via.placeholder.com/150",
    },
]

st.markdown(
    """
    <h1 style="line-height:1.2; text-align:center;">
      <span style="font-size:60px; color:#4e79a7;">🎓AI College</span><br>
      <span style="font-size:50px;">Exploration</span>
    </h1>
    <p style="text-align:center; font-size:20px; color:#555;">
      Your AI-powered multi-agent guide through the university application process.
    </p>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# --- Features section ---
st.markdown("<h2>🚀 Features</h2>", unsafe_allow_html=True)

# First Row
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
        #### 📝 Essay Writing Assistant
        - Structure and refine personal and supplemental essays
        - Grammar, tone, and clarity improvements
        - Real-time, university-specific feedback
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        #### 📊 Program Analysis
        - Compare programs side-by-side
        - Analyze cost, ranking, curriculum & career outcomes
        - Actionable recommendations
        """,
        unsafe_allow_html=True,
    )

# Second Row
col3, col4 = st.columns(2)
with col3:
    st.markdown(
        """
        #### 🕵️ Sentiment Analysis
        - Analyze student feedback from Reddit & forums
        - Summarize insights on academics, campus life & more
        """,
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        """
        #### 💵 Cost Breakdown
        - Personalized cost estimate for a selected university
        - Includes tuition, accommodation, living, visa, travel, and other expenses
        """,
        unsafe_allow_html=True,
    )

# Third Row
col5, col6 = st.columns(2)
with col5:
    st.markdown(
        """
        #### 🗓️ Timeline Planner
        - Visualize deadlines and interview schedules
        - Suggests optimal dates for task completion
        """,
        unsafe_allow_html=True,
    )
with col6:
    st.markdown(
        """
        #### 📋 Checklist Generator
        - Dynamic document checklists for each university
        - Tailored by applicant profile and program needs
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- Team section ---
st.markdown("<h2>🤝 Our Team</h2>", unsafe_allow_html=True)
rows = [team_members[:3]]
for row in rows:
    cols = st.columns(len(row))
    for i, member in enumerate(row):
        with cols[i]:
            st.image(member["image_url"], width=120, caption=member["name"])
            st.markdown(
                f"<p style='color:#555; margin-top:-10px;'>{member['role']}</p>",
                unsafe_allow_html=True,
            )
            if member["github"] != "#":
                st.markdown(f"[github]({member['github']})", unsafe_allow_html=True)
st.markdown("---")

# --- Timeline section ---
st.markdown("<h2>📅 Timeline</h2>", unsafe_allow_html=True)
cols = st.columns(len(timeline))
for idx, item in enumerate(timeline):
    with cols[idx]:
        date = item["date"]
        color = (
            "#4e79a7"
            if date == today
            else ("#4e79a7" if date and date < today else "#ccc")
        )
        st.markdown(
            f"""
            <div style="
              width: 16px; height: 16px; border-radius: 8px;
              background:{color}; margin:0 auto;
              border:2px solid {'#333' if date == today else color};
            "></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='font-size:14px; text-align:center; color:#555; margin-top:5px;'>{item['event']}</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='font-size:12px; text-align:center; color:#999; margin-top:-8px;'>{date or 'Upcoming'}</p>",
            unsafe_allow_html=True,
        )
# connecting line
st.markdown(
    """
    <div style='position:relative; width:100%; margin-top:-10px;'>
      <div style='width:90%; height:2px; background:#ddd; margin:0 auto;'></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# --- Footer ---
year = datetime.now().year
st.markdown(
    f"""
    <p style="text-align:center; color:#999; font-size:14px;">
      &copy; {year} AI College Exploration (AICE). All rights reserved.
    </p>
    """,
    unsafe_allow_html=True,
)
