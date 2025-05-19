# app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

import db
from generate_run import generate_college_exploration_background

app = FastAPI(
    title="AI College Exploration (AICE) API",
    version="0.1.0",
    description="Backend for the AICE multi-agent system",
)

# CORS (development only—lock this down in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/sessions/essay")
def start_essay_session(payload: Dict[str, Any]):
    """
    Start an essay-writing session.
    Expects JSON with:
      - user_id: str
      - essay_text: str
      - target_university: str
      - style_guidelines: str
    Returns:
      - session_id: str
    """
    user_id = payload.get("user_id")
    essay_text = payload.get("essay_text")
    target_university = payload.get("target_university")
    style_guidelines = payload.get("style_guidelines")

    if not all([user_id, essay_text, target_university, style_guidelines]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Create DB session
    session_id = db.create_essay_session(user_id, essay_text, target_university)

    # Kick off background flow
    generate_college_exploration_background(
        session_id,
        {
            "flow_type": "essay",
            "essay_text": essay_text,
            "target_university": target_university,
            "style_guidelines": style_guidelines,
        },
    )

    return {"session_id": session_id}


@app.get("/sessions/essay/{session_id}/status")
def get_essay_status(session_id: str):
    """
    Get the current status of an essay-writing session.
    Returns status = one of ["pending","in_progress","completed","failed"].
    """
    sess = db.get_essay_session(session_id)
    resp = {
        "session_id": session_id,
        "status": sess["status"],
    }
    if sess["status"] == "failed":
        resp["error"] = sess.get("error", "Unknown error")
    return resp


@app.get("/sessions/essay/{session_id}/result")
def get_essay_result(session_id: str):
    """
    Fetch outline + refined draft after completion.
    Returns:
      - outline: Any
      - refined_draft: str
    """
    results = db.get_essay_results(session_id)
    return {
        "outline": results["outline"],
        "refined_draft": results["refined_draft"],
    }


@app.post("/sessions/program-analysis")
def start_program_analysis(payload: Dict[str, Any]):
    """
    Start a program-analysis session.
    Expects JSON with:
      - user_id: str
      - university_list: List[str]
      - comparison_criteria: List[str]
    Returns:
      - session_id: str
    """
    user_id = payload.get("user_id")
    university_list = payload.get("university_list")
    comparison_criteria = payload.get("comparison_criteria")

    if not user_id or not isinstance(university_list, list) or not isinstance(comparison_criteria, list):
        raise HTTPException(status_code=400, detail="Missing or invalid fields")

    session_id = db.create_program_analysis_session(user_id, university_list, comparison_criteria)

    generate_college_exploration_background(
        session_id,
        {
            "flow_type": "program_analysis",
            "university_list": university_list,
            "comparison_criteria": comparison_criteria,
        },
    )

    return {"session_id": session_id}


@app.get("/sessions/program-analysis/{session_id}/status")
def get_program_analysis_status(session_id: str):
    """
    Get the current status of a program-analysis session.
    """
    sess = db.get_program_analysis_session(session_id)
    return {"session_id": session_id, "status": sess["status"]}


@app.get("/sessions/program-analysis/{session_id}/result")
def get_program_analysis_result(session_id: str):
    """
    Fetch raw data, structured data, and comparison report after completion.
    """
    raw = db.get_raw_admissions_data(session_id)
    structured = db.get_structured_admissions_data(session_id)
    report = db.get_program_comparison_report(session_id)
    return {
        "raw_admissions_data": raw,
        "structured_admissions_data": structured,
        "program_comparison_report": report,
    }
