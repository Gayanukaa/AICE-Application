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
    preferences: str
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


