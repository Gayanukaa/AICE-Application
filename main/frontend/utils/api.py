import httpx
from utils.constants import API_BASE_URL


def create_essay_session(
    user_id: str, essay_text: str, target_university: str, style_guidelines: str
) -> str:
    """
    POST /sessions/essay
    Returns the new session_id.
    """
    payload = {
        "user_id": user_id,
        "essay_text": essay_text,
        "target_university": target_university,
        "style_guidelines": style_guidelines,
    }
    resp = httpx.post(f"{API_BASE_URL}/sessions/essay", json=payload)
    resp.raise_for_status()
    return resp.json()["session_id"]


def get_essay_status(session_id: str) -> dict:
    """
    GET /sessions/essay/{session_id}/status
    Returns {"session_id": ..., "status": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/essay/{session_id}/status")
    resp.raise_for_status()
    return resp.json()


def get_essay_result(session_id: str) -> dict:
    """
    GET /sessions/essay/{session_id}/result
    Returns {"outline": ..., "refined_draft": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/essay/{session_id}/result")
    resp.raise_for_status()
    return resp.json()


def create_program_analysis_session(
    user_id: str, university_list: list, comparison_criteria: list
) -> str:
    """
    POST /sessions/program-analysis
    Returns the new session_id.
    """
    payload = {
        "user_id": user_id,
        "university_list": university_list,
        "comparison_criteria": comparison_criteria,
    }
    resp = httpx.post(f"{API_BASE_URL}/sessions/program-analysis", json=payload)
    resp.raise_for_status()
    return resp.json()["session_id"]


def get_program_analysis_status(session_id: str) -> dict:
    """
    GET /sessions/program-analysis/{session_id}/status
    Returns {"session_id": ..., "status": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/program-analysis/{session_id}/status")
    resp.raise_for_status()
    return resp.json()


def get_program_analysis_result(session_id: str) -> dict:
    """
    GET /sessions/program-analysis/{session_id}/result
    Returns {"raw_admissions_data": ..., "structured_admissions_data": ..., "program_comparison_report": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/program-analysis/{session_id}/result")
    resp.raise_for_status()
    return resp.json()


def sentiment_analysis(reviews: list[str]) -> dict:
    """
    POST /sentiment-analysis
    Input: {"reviews": [...]}
    Output: {"reddit_posts": [...], "summary": "..."}
    """
    resp = httpx.post(
        f"{API_BASE_URL}/sentiment-analysis",
        json={"reviews": reviews},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()


def create_cost_breakdown_session(
    user_id: str,
    university: str,
    course: str,
    applicant_type: str,
    location: str,
    preferences: str,
) -> str:
    """
    POST /sessions/cost-breakdown
    Returns the new session_id.
    """
    payload = {
        "user_id": user_id,
        "university": university,
        "course": course,
        "applicant_type": applicant_type,
        "location": location,
        "preferences": preferences,
    }
    resp = httpx.post(f"{API_BASE_URL}/sessions/cost-breakdown", json=payload)
    resp.raise_for_status()
    return resp.json()["session_id"]


def get_cost_breakdown_status(session_id: str) -> dict:
    """
    GET /sessions/cost-breakdown/{session_id}/status
    Returns {"session_id": ..., "status": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/cost-breakdown/{session_id}/status")
    resp.raise_for_status()
    return resp.json()


def get_cost_breakdown_result(session_id: str) -> dict:
    """
    GET /sessions/cost-breakdown/{session_id}/result
    Returns {"expenses": ..., "total": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/cost-breakdown/{session_id}/result")

    resp.raise_for_status()
    return resp.json()


def create_timeline_planner_session(
    user_id: str,
    universities: list,
    level: str,
    applicant_type: str,
    nationality: str,
    intake: str,
    applicant_availability: str,
) -> str:
    """
    POST /sessions/timeline
    Returns the new session_id or error information.
    """
    payload = {
        "user_id": user_id,
        "universities": universities,
        "level": level,
        "applicant_type": applicant_type,
        "nationality": nationality,
        "intake": intake,
        "applicant_availability": applicant_availability,
    }
    try:
        resp = httpx.post(f"{API_BASE_URL}/sessions/timeline", json=payload)
        resp.raise_for_status()
        return resp.json()["session_id"]
    except httpx.HTTPStatusError as exc:
        return {
            "error": "HTTPStatusError",
            "status_code": exc.response.status_code,
            "response_text": exc.response.text,
            "payload": payload,
        }


def get_timeline_status(session_id: str) -> dict:
    """
    GET /sessions/timeline/{session_id}/status
    Returns {"session_id": ..., "status": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/timeline/{session_id}/status")
    resp.raise_for_status()
    return resp.json()


def get_timeline_result(session_id: str) -> dict:
    """
    GET /sessions/timeline/{session_id}/result
    Returns timeline results.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/timeline/{session_id}/result")
    resp.raise_for_status()
    return resp.json()


def create_checklist_session(
    user_id: str, nationality: str, program_level: str, universities: list
) -> str:
    """
    POST /sessions/checklist
    Returns the new session_id or error information.
    """
    payload = {
        "user_id": user_id,
        "nationality": nationality,
        "program_level": program_level,
        "university_list": universities,
    }
    try:
        resp = httpx.post(f"{API_BASE_URL}/sessions/checklist", json=payload)
        resp.raise_for_status()
        return resp.json()["session_id"]
    except httpx.HTTPStatusError as exc:
        return {
            "error": "HTTPStatusError",
            "status_code": exc.response.status_code,
            "response_text": exc.response.text,
            "payload": payload,
        }


def get_checklist_status(session_id: str) -> dict:
    """
    GET /sessions/checklist/{session_id}/status
    Returns {"session_id": ..., "status": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/checklist/{session_id}/status")
    resp.raise_for_status()
    return resp.json()


def get_checklist_result(session_id: str) -> dict:
    """
    GET /sessions/checklist/{session_id}/result
    Returns {"dynamic_checklist": ...}.
    """
    resp = httpx.get(f"{API_BASE_URL}/sessions/checklist/{session_id}/result")
    resp.raise_for_status()
    return resp.json()
