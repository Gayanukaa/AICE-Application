# frontend/components/result_display.py

import time
import pandas as pd


import streamlit as st
from utils.api import (
    get_essay_result,
    get_essay_status,
    get_program_analysis_result,
    get_program_analysis_status,
    get_cost_breakdown_result,
    get_cost_breakdown_status,

)


def display_essay_results(session_id: str, timeout: int = 60, interval: float = 2.0):
    """Poll with a spinner, then render results for an essay-writing session."""
    st.subheader("📝 Essay Writing Results")

    status = None
    start = time.time()
    with st.spinner("Waiting for the essay agents to finish…"):
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
        st.write(paragraph)
        st.markdown("")  # paragraph spacing


def display_program_analysis_results(
    session_id: str, timeout: int = 60, interval: float = 2.0
):
    """Poll with a spinner, then nicely render program-analysis outputs."""
    st.subheader("📊 Program Analysis Results")

    # --- Polling loop ---
    status = None
    start = time.time()
    with st.spinner("Waiting for the program-analysis agents to finish…"):
        while time.time() - start < timeout:
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
        {"Fee Name": name, f"Amount ({currency})": int(info["amount"])}
        for name, info in expenses.items()
    ]
    # Append total cost row
    table_data.append(
        {"Fee Name": "Estimated Total", f"Amount ({currency})": total_cost}
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
      