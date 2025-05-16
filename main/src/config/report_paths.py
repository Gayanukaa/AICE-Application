"""Defines file paths for AICE project outputs."""

import os

REPORT_DIR = os.path.join("src", "data", "report", "{session_id}")

ESSAY_OUTLINE_FILE = os.path.join(REPORT_DIR, "essay_outlines.md")
REFINED_ESSAY_FILE = os.path.join(REPORT_DIR, "refined_essays.md")
RAW_ADMISSIONS_DATA_FILE = os.path.join(REPORT_DIR, "raw_admissions_data.json")
STRUCTURED_ADMISSIONS_DATA_FILE = os.path.join(REPORT_DIR, "structured_admissions_data.json")
PROGRAM_COMPARISON_REPORT_FILE = os.path.join(REPORT_DIR, "program_comparison_report.md")
