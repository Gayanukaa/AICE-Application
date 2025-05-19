# frontend/components/result_display.py

import time
import streamlit as st
from utils.api import (
    get_essay_status,
    get_essay_result,
    get_program_analysis_status,
    get_program_analysis_result,
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
    session_id: str,
    timeout: int = 60,
    interval: float = 2.0
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

    # 1. Raw Admissions Data
    st.markdown("### 1. Raw Admissions Data")
    raw = res.get("raw_admissions_data", {})
    # some payloads wrap under "raw_data" key
    raw = raw.get("raw_data", raw)
    for uni, uni_data in raw.items():
        st.markdown(f"**{uni}**")
        for category, details in uni_data.items():
            st.markdown(f"*{category}*")
            if isinstance(details, dict):
                for subcat, items in details.items():
                    st.markdown(f"    **{subcat}**")
                    if isinstance(items, list):
                        for item in items:
                            st.markdown(f"        - {item}")
                    elif isinstance(items, dict):
                        for k, v in items.items():
                            st.markdown(f"        - {k}: {v}")
                    else:
                        st.markdown(f"        - {items}")
            elif isinstance(details, list):
                for item in details:
                    st.markdown(f"    - {item}")
            else:
                st.markdown(f"    - {details}")
        st.write("")

    # 2. Structured Admissions Data
    st.markdown("### 2. Structured Admissions Data")
    structured = res.get("structured_admissions_data", {})
    for uni, uni_data in structured.items():
        st.markdown(f"**{uni}**")
        if isinstance(uni_data, dict):
            for field, val in uni_data.items():
                st.markdown(f"*{field}*")
                if isinstance(val, list):
                    for item in val:
                        st.markdown(f"    - {item}")
                elif isinstance(val, dict):
                    for k, v in val.items():
                        if isinstance(v, list):
                            st.markdown(f"    **{k}**")
                            for ii in v:
                                st.markdown(f"        - {ii}")
                        else:
                            st.markdown(f"    - {k}: {v}")
                else:
                    st.markdown(f"    - {val}")
        else:
            st.markdown(f"- {uni_data}")
        st.write("")

    # 3. Program Comparison Report
    st.markdown("### 3. Program Comparison Report")
    report = res.get("comparison_report", {})
    if isinstance(report, dict):
        for section, content in report.items():
            st.markdown(f"**{section}**")
            if isinstance(content, dict):
                for uni, metrics in content.items():
                    st.markdown(f"    *{uni}*")
                    if isinstance(metrics, dict):
                        for metric, val in metrics.items():
                            if isinstance(val, list):
                                st.markdown(f"        **{metric}**")
                                for item in val:
                                    st.markdown(f"            - {item}")
                            else:
                                st.markdown(f"        - {metric}: {val}")
                    else:
                        st.markdown(f"        - {metrics}")
            else:
                st.markdown(f"- {content}")
            st.write("")
    else:
        st.error(f"⚠️ Invalid comparison report: {report}")
