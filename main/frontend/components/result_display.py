# frontend/components/result_display.py

import time

import streamlit as st
from utils.api import (
    get_essay_result,
    get_essay_status,
    get_program_analysis_result,
    get_program_analysis_status,
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
