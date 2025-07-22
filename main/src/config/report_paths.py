import os

REPORT_DIR = os.path.join("data", "report", "{session_id}")

ESSAY_OUTLINE_FILE = os.path.join(REPORT_DIR, "essay_outlines.md")
REFINED_ESSAY_FILE = os.path.join(REPORT_DIR, "refined_essays.md")
RAW_ADMISSIONS_DATA_FILE = os.path.join(REPORT_DIR, "raw_admissions_data.json")
STRUCTURED_ADMISSIONS_DATA_FILE = os.path.join(
    REPORT_DIR, "structured_admissions_data.json"
)
PROGRAM_COMPARISON_REPORT_FILE = os.path.join(
    REPORT_DIR, "program_comparison_report.md"
)
DYNAMIC_CHECKLIST_FILE = os.path.join(REPORT_DIR, "dynamic_checklist.md")
RAW_FEES_FILE = os.path.join(REPORT_DIR, "raw_fees.json")
COST_BREAKDOWN_FILE = os.path.join(REPORT_DIR, "cost_breakdown.json")
DEADLINES_FILE = os.path.join(REPORT_DIR, "deadlines.json")
TIMELINE_FILE = os.path.join(REPORT_DIR, "timeline.json")
INTERVIEW_RESEARCH_FILE = os.path.join(REPORT_DIR, "interview_research.json")
INTERVIEW_QA_FILE = os.path.join(REPORT_DIR, "interview_qa.json")