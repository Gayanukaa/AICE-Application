# frontend/components/result_display.py

import json
import time

import pandas as pd
import streamlit as st
from streamlit_timeline import timeline
from utils.api import (
    get_checklist_result,
    get_checklist_status,
    get_cost_breakdown_result,
    get_cost_breakdown_status,
    get_essay_result,
    get_essay_status,
    get_program_analysis_result,
    get_program_analysis_status,
    get_timeline_result,
    get_timeline_status,
)


def stream_paragraph(paragraph):
    for word in paragraph.split():
        yield word + " "
        time.sleep(0.05)


def display_essay_results(session_id: str, timeout: int = 60, interval: float = 2.0):
    """Poll with a spinner, then render results for an essay-writing session."""
    st.subheader("📝 Essay Writing Results")

    status = None
    start = time.time()
    with st.spinner("Essay agents in action…"):
        while time.time() - start < timeout:
            resp = get_essay_status(session_id)
            if resp["status"] in ("completed", "failed"):
                status = resp
                break
            time.sleep(interval)

    if status is None:
        st.error("⏱️ Timed out waiting for results. Try refreshing.")
        return

    st.write(f"**Status:** {status['status'].capitalize()}")

    if status["status"] == "failed":
        st.error(f"⚠️ Error: {status.get('error', 'Unknown error')}")
        return

    # Completed: fetch results
    res = get_essay_result(session_id)

    # Unwrap outline & refined essay
    outline = res.get("outline", {})
    refined_data = res.get("refined_draft", "")
    # If it came back as a dict, extract the text
    if isinstance(refined_data, dict):
        refined_text = refined_data.get("refined_draft", "")
    else:
        refined_text = refined_data or ""

    # Structured Outline
    st.markdown("### 🗂 Structured Outline")
    for section, bullets in outline.items():
        st.markdown(f"**{section}**")
        for item in bullets:
            st.markdown(f"    - {item}")  # indented bullet
        st.markdown("")  # extra spacing

    # Refined Essay
    st.markdown("### ✍️ Refined Essay")

    for paragraph in refined_text.split("\n\n"):
        st.write_stream(stream_paragraph(paragraph))
        st.markdown("")


def display_program_analysis_results(
    session_id: str, timeout: int = 120, interval: float = 2.0
):
    """Poll with a spinner, then nicely render program-analysis outputs."""
    st.subheader("📊 Program Analysis Results")

    # --- Polling loop ---
    status = None
    start = time.time()
    warned = False  # To track if the 1-minute message has been shown

    with st.spinner("Waiting for the program-analysis agents to finish…"):
        while time.time() - start < timeout:
            elapsed = time.time() - start

            if elapsed > 60 and not warned:
                st.info("⏳ Still working... Extracting a large amount of content. Please wait a bit longer.")
                warned = True

            resp = get_program_analysis_status(session_id)
            if resp["status"] in ("completed", "failed"):
                status = resp
                break
            time.sleep(interval)

    if status is None:
        st.error("⏱️ Timed out waiting for results. Try refreshing.")
        return

    st.write(f"**Status:** {status['status'].capitalize()}")

    if status["status"] == "failed":
        st.error(f"⚠️ Error: {status.get('error', 'Unknown error')}")
        return

    # --- Fetch results ---
    res = get_program_analysis_result(session_id)

    report = res.get("program_comparison_report", {})
    if isinstance(report, dict):
        lines = report["comparison_report"].strip().splitlines()
        markdown_content = "\n".join(lines[1:])
        st.markdown(markdown_content)
    else:
        st.error(f"⚠️ Invalid comparison report: {report}")


def display_cost_breakdown_results(
    session_id: str, timeout: int = 60, interval: float = 2.0
):
    """Poll with a spinner, then nicely render program-analysis outputs."""
    st.subheader("📊 Cost Breakdown  Results")

    if "breakdown" not in st.session_state:
        status = None
        start = time.time()
        with st.spinner("Waiting for the cost breakdown agents to finish…"):
            while time.time() - start < timeout:
                resp = get_cost_breakdown_status(session_id)
                if resp["status"] in ("completed", "failed"):
                    status = resp
                    break
                time.sleep(interval)

        if status is None:
            st.error("⏱️ Timed out waiting for results. Try refreshing.")
            return

        st.write(f"**Status:** {status['status'].capitalize()}")

        if status["status"] == "failed":
            st.error(f"⚠️ Error: {status.get('error', 'Unknown error')}")
            return

        st.session_state.breakdown = get_cost_breakdown_result(session_id)
    # --- Fetch results ---

    breakdown = st.session_state.breakdown
    expenses = breakdown["expenses"]
    currency = breakdown["currency"]
    total_cost = breakdown["total_cost"]

    # Construct table data
    table_data = [
        {"Fee Name": name, f"Amount ({currency})": round(int(info["amount"]) / 100) * 100}
        for name, info in expenses.items()
    ]
    # Append total cost row
    table_data.append(
        {"Fee Name": "Estimated Total", f"Amount ({currency})": round(int(total_cost) / 100) * 100}
    )

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Fee Table")
        st.table(table_data)

    with col2:
        st.markdown("### View Description")
        selected_fee = st.selectbox("Select a fee", list(expenses.keys()))
        if selected_fee:
            st.markdown("---")
            st.markdown(f"**{selected_fee}**")
            st.info(expenses[selected_fee]["description"])


def display_timeline_planner_results(
    session_id: str, timeout: int = 60, interval: float = 2.0
):
    """Poll with a spinner, then nicely render program-analysis outputs."""
    st.subheader("📊 Timeline Planner Results")

    status = None
    start = time.time()
    with st.spinner("Waiting for the program-analysis agents to finish…"):
        while time.time() - start < timeout:
            resp = get_timeline_status(session_id)
            if resp["status"] in ("completed", "failed"):
                status = resp
                break
            time.sleep(interval)

    if status is None:
        st.error("⏱️ Timed out waiting for results. Try refreshing.")
        return

    st.write(f"**Status:** {status['status'].capitalize()}")

    if status["status"] == "failed":
        st.error(f"⚠️ Error: {status.get('error', 'Unknown error')}")
        return

    response = get_timeline_result(session_id)

    # Deadlines
    st.header("University Deadlines")
    for uni in response["deadlines"]:
        st.subheader(uni["university"])

        interview_periods_raw = uni.get("interview_periods", [])
        interview_periods = [
            f"{p['start']} to {p['end']}"
            for p in interview_periods_raw
            if p.get("start") and p.get("end")
        ] or ["No deadlines found"]

        deadline_table = {
            "Application Start": uni.get("application_start") or "No deadlines found",
            "Application End": uni.get("application_end") or "No deadlines found",
            "Essay Deadline": uni.get("essay_deadline") or "No deadlines found",
            "Interview Periods": interview_periods,
            "Scholarship Deadlines": uni.get("scholarship_deadlines")
            or ["No deadlines found"],
        }

        formatted_deadline_table = {
            k: v if isinstance(v, str) else ", ".join(v)
            for k, v in deadline_table.items()
        }

        df = pd.DataFrame(
            list(formatted_deadline_table.items()), columns=["Deadline Type", "Date(s)"]
        )
        st.table(df)

    if not response["timeline"]["deadlines"] and not response["timeline"]["events"] and not response["timeline"]["suggestions"]:
        st.warning(
            "🚫 Relevant deadlines for the selected intake have already passed. "
            "A personalized timeline could not be created. "
            "Try selecting a future intake period."
        )
        return
    
    # Timeline
    timeline_events = []

    # Process events
    for event in response["timeline"]["events"]:
        try:
            year, month, day = map(int, event["date"].split("-"))
            timeline_events.append(
                {
                    "start_date": {"year": year, "month": month, "day": day},
                    "text": {"text": event["task"]},
                    "background": {"color": "#2E2E2E"},
                    "group": "Timeline",
                }
            )
        except (ValueError, AttributeError):
            st.warning(f"Invalid date format for event: {event}")

    # Process deadlines
    for deadline in response["timeline"]["deadlines"]:
        try:
            year, month, day = map(int, deadline["date"].split("-"))
            timeline_events.append(
                {
                    "start_date": {"year": year, "month": month, "day": day},
                    "text": {"headline": deadline["name"]},
                    "background": {"color": "#8A041E"},
                    "group": "Timeline",
                }
            )
        except (ValueError, AttributeError):
            st.warning(f"Invalid date format for deadline: {deadline}")

    # Timeline visualization
    timeline_data = {
        "title": {"text": {"text": "Application Timeline"}},
        "events": timeline_events,
    }

    st.header("Timeline")
    timeline(json.dumps(timeline_data), height=500)

    # Suggestions section
    st.header("Suggestions")
    suggestion_lines = [
        f"- **{s['task']}** — _{s['recommended_date']}_"
        for s in response["timeline"]["suggestions"]
    ]
    st.markdown("\n".join(suggestion_lines))


def display_checklist_results(
    session_id: str, timeout: int = 60, interval: float = 2.0
):
    """Poll with a spinner, then render results for the dynamic application checklist."""
    st.subheader("📋 Application Checklist Results")

    status = None
    start = time.time()
    with st.spinner("Waiting for the checklist agents to finish…"):
        while time.time() - start < timeout:
            resp = get_checklist_status(session_id)
            if resp["status"] in ("completed", "failed"):
                status = resp
                break
            time.sleep(interval)

    if status is None:
        st.error("⏱️ Timed out waiting for results. Try refreshing.")
        return

    st.write(f"**Status:** {status['status'].capitalize()}")

    if status["status"] == "failed":
        st.error(f"⚠️ Error: {status.get('error', 'Unknown error')}")
        return

    # Completed: fetch results
    response = get_checklist_result(session_id)
    result = response.get("dynamic_checklist", {})
    checklists = result.get("checklists", [])

    if not checklists:
        st.warning("No checklists found.")
        return

    # Display each university's checklist
    for uni_checklist in checklists:
        st.markdown(f"## 🎓 {uni_checklist['university'].upper()}")
        for idx, item in enumerate(uni_checklist["items"], start=1):
            doc = item["document"]
            required = "✅ Required" if item["required"] else "🟡 Optional"
            notes = item.get("notes", "")
            with st.container():
                st.markdown(f"**{idx}. 📄 {doc}**  \n{required}")
                if notes:
                    st.info(notes)
        st.markdown("---")
