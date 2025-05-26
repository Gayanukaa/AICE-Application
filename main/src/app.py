from typing import Any, Dict, List

import db
from config.models import RedditPost, SentimentRequest, SentimentResponse
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from generate_run import generate_college_exploration_background
from generate_run import generate_application_planning_background
from pydantic import BaseModel
from utils.sentiment_utils import sentiment_reddit_summary

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
def start_essay_session(payload: Dict[str, Any], background_tasks: BackgroundTasks):
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
    background_tasks.add_task(
        generate_college_exploration_background,
        session_id,
        {
            "flow_type": "essay",
            "essay_text": essay_text,
            "target_university": target_university,
            "style_guidelines": style_guidelines,
        },
    )

    # return immediately
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
def start_program_analysis(payload: Dict[str, Any], background_tasks: BackgroundTasks):
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

    if (
        not user_id
        or not isinstance(university_list, list)
        or not isinstance(comparison_criteria, list)
    ):
        raise HTTPException(status_code=400, detail="Missing or invalid fields")

    session_id = db.create_program_analysis_session(
        user_id, university_list, comparison_criteria
    )

    background_tasks.add_task(
        generate_college_exploration_background,
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

# --- Dynamic Checklist (Feature 4) ------------------------------------------

@app.post("/sessions/checklist")
def start_dynamic_checklist(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Start a Dynamic Application Checklist session.
    Expects JSON with:
      - user_id: str
      - nationality: str
      - program_level: str
      - university_list: List[str]
    Returns:
      - session_id: str
    """
    user_id = payload.get("user_id")
    nationality = payload.get("nationality")
    program_level = payload.get("program_level")
    university_list = payload.get("university_list")

    if not user_id \
       or not isinstance(nationality, str) \
       or not isinstance(program_level, str) \
       or not isinstance(university_list, list):
        raise HTTPException(status_code=400, detail="Missing or invalid fields")

    session_id = db.create_checklist_session(user_id, nationality, program_level, university_list)

    background_tasks.add_task(
        generate_application_planning_background,
        session_id,
        {
            "flow_type": "dynamic_checklist",
            "nationality": nationality,
            "program_level": program_level,
            "university_list": university_list,
        },
    )

    return {"session_id": session_id}


@app.get("/sessions/checklist/{session_id}/status")
def get_dynamic_checklist_status(session_id: str):
    """
    Get the current status of a Dynamic Checklist session.
    """
    sess = db.get_checklist_session(session_id)
    return {"session_id": session_id, "status": sess["status"]}


@app.get("/sessions/checklist/{session_id}/result")
def get_dynamic_checklist_result(session_id: str):
    """
    Fetch the final checklist after completion.
    """
    checklist = db.get_dynamic_checklist(session_id)
    return {"dynamic_checklist": checklist}


# --- Cost Breakdown (Feature 5) --------------------------------------------

@app.post("/sessions/cost-breakdown")
def start_cost_breakdown(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Start a Personalized Cost Breakdown session.
    Expects JSON with:
      - user_id: str
      - university_list: List[str]
      - program_level: str
      - user_budget: float
      - destination: str
    Returns:
      - session_id: str
    """
    user_id = payload.get("user_id")
    university_list = payload.get("university_list")
    program_level = payload.get("program_level")
    user_budget = payload.get("user_budget")
    destination = payload.get("destination")

    if not user_id \
       or not isinstance(university_list, list) \
       or not isinstance(program_level, str) \
       or not isinstance(user_budget, (int, float)) \
       or not isinstance(destination, str):
        raise HTTPException(status_code=400, detail="Missing or invalid fields")

    session_id = db.create_cost_breakdown_session(
        user_id, university_list, program_level, user_budget, destination
    )

    background_tasks.add_task(
        generate_application_planning_background,
        session_id,
        {
            "flow_type": "cost_breakdown",
            "university_list": university_list,
            "program_level": program_level,
            "user_budget": user_budget,
            "destination": destination,
        },
    )

    return {"session_id": session_id}


@app.get("/sessions/cost-breakdown/{session_id}/status")
def get_cost_breakdown_status(session_id: str):
    """
    Get the current status of a Cost Breakdown session.
    """
    sess = db.get_cost_breakdown_session(session_id)
    return {"session_id": session_id, "status": sess["status"]}


@app.get("/sessions/cost-breakdown/{session_id}/result")
def get_cost_breakdown_result(session_id: str):
    """
    Fetch fee data and cost breakdown after completion.
    """
    fees = db.get_fee_data(session_id)
    breakdown = db.get_cost_breakdown(session_id)
    return {
        "fee_data": fees,
        "cost_breakdown": breakdown,
    }


# --- Timeline Planner (Feature 6) ------------------------------------------

@app.post("/sessions/timeline")
def start_timeline_planner(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Start an Interactive Application Timeline session.
    Expects JSON with:
      - user_id: str
      - university_list: List[str]
      - program_level: str
      - applicant_availability: Optional[str]
    Returns:
      - session_id: str
    """
    user_id = payload.get("user_id")
    university_list = payload.get("university_list")
    program_level = payload.get("program_level")
    applicant_availability = payload.get("applicant_availability")

    if not user_id \
       or not isinstance(university_list, list) \
       or not isinstance(program_level, str):
        raise HTTPException(status_code=400, detail="Missing or invalid fields")

    session_id = db.create_timeline_session(
        user_id, university_list, program_level, applicant_availability
    )

    background_tasks.add_task(
        generate_application_planning_background,
        session_id,
        {
            "flow_type": "timeline",
            "university_list": university_list,
            "program_level": program_level,
            "applicant_availability": applicant_availability,
        },
    )

    return {"session_id": session_id}


@app.get("/sessions/timeline/{session_id}/status")
def get_timeline_status(session_id: str):
    """
    Get the current status of a Timeline Planner session.
    """
    sess = db.get_timeline_session(session_id)
    return {"session_id": session_id, "status": sess["status"]}


@app.get("/sessions/timeline/{session_id}/result")
def get_timeline_result(session_id: str):
    """
    Fetch extracted deadlines and generated timeline after completion.
    """
    deadlines = db.get_deadline_data(session_id)
    timeline = db.get_timeline(session_id)
    return {
        "deadlines": deadlines,
        "timeline": timeline,
    }


@app.post(
    "/sentiment-analysis",
    response_model=SentimentResponse,
    summary="Fetch related Reddit posts & AI‐summarize sentiment",
)
async def sentiment_analysis(payload: SentimentRequest):
    """
    Input JSON:
        { "reviews": ["Review text here"] }

    Returns:
        {
          "reddit_posts": [ {"title": ..., "url": ...}, … ],
          "summary": "3–4 sentence summary …"
        }
    """
    return sentiment_reddit_summary(payload.reviews)
