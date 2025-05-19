import datetime
import json
import os
import uuid
from typing import Any, Dict, List

# Path to JSON‐backed datastore
DB_FILENAME = os.path.join(os.path.dirname(__file__), "aice_db.json")


def read_db() -> Dict[str, Any]:
    """Load the entire database, creating defaults if necessary."""
    if not os.path.exists(DB_FILENAME):
        default = {
            "users": {},
            "essay_writing_sessions": {},
            "essay_results": {},
            "program_analysis_sessions": {},
            "raw_admissions_data": {},
            "structured_admissions_data": {},
            "program_comparison_reports": {},
        }
        update_db(default)
        return default

    with open(DB_FILENAME, "r") as f:
        return json.load(f)


def update_db(db: Dict[str, Any]) -> None:
    """Persist the given database state to disk."""
    with open(DB_FILENAME, "w") as f:
        json.dump(db, f, indent=4, default=str)


#
# User CRUD
#
def create_user(user_data: Dict[str, Any]) -> str:
    """Register a new user and return its user_id."""
    db = read_db()
    user_id = str(uuid.uuid4())
    db["users"][user_id] = user_data
    update_db(db)
    return user_id


def get_user(user_id: str) -> Dict[str, Any]:
    """Retrieve a user record, or raise if not found."""
    db = read_db()
    if user_id not in db["users"]:
        raise KeyError(f"User {user_id} not found")
    return db["users"][user_id]


def update_user(user_id: str, updates: Dict[str, Any]) -> None:
    """Apply updates to an existing user."""
    db = read_db()
    if user_id not in db["users"]:
        raise KeyError(f"User {user_id} not found")
    db["users"][user_id].update(updates)
    update_db(db)


def delete_user(user_id: str) -> None:
    """Remove a user and all their related sessions/results."""
    db = read_db()
    db["users"].pop(user_id, None)
    # also cascade‐delete any sessions/results for that user
    for collection in (
        "essay_writing_sessions",
        "essay_results",
        "program_analysis_sessions",
        "raw_admissions_data",
        "structured_admissions_data",
        "program_comparison_reports",
    ):
        to_remove = [
            sid
            for sid, record in db.get(collection, {}).items()
            if record.get("user_id") == user_id
        ]
        for sid in to_remove:
            db[collection].pop(sid, None)
    update_db(db)


def create_essay_session(user_id: str, essay_text: str, target_university: str) -> str:
    """Start a new essay-writing session and return its session_id."""
    db = read_db()
    session_id = str(uuid.uuid4())
    db["essay_writing_sessions"][session_id] = {
        "user_id": user_id,
        "essay_text": essay_text,
        "target_university": target_university,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "status": "pending",
    }
    update_db(db)
    return session_id


def get_essay_session(session_id: str) -> Dict[str, Any]:
    """Fetch essay-writing session details."""
    db = read_db()
    if session_id not in db["essay_writing_sessions"]:
        raise KeyError(f"Essay session {session_id} not found")
    return db["essay_writing_sessions"][session_id]


def save_essay_results(session_id: str, outline: Any, refined_draft: str) -> None:
    """Store outline and refined draft, and mark the session completed."""
    db = read_db()
    if session_id not in db["essay_writing_sessions"]:
        raise KeyError(f"Essay session {session_id} not found")
    db["essay_results"][session_id] = {
        "outline": outline,
        "refined_draft": refined_draft,
        "completed_at": datetime.datetime.utcnow().isoformat(),
    }
    # mark session completed
    db["essay_writing_sessions"][session_id]["status"] = "completed"
    update_db(db)


def get_essay_results(session_id: str) -> Dict[str, Any]:
    """Retrieve saved essay results (outline + refined draft)."""
    db = read_db()
    if session_id not in db["essay_results"]:
        raise KeyError(f"No results for essay session {session_id}")
    return db["essay_results"][session_id]


def delete_essay_session(session_id: str) -> None:
    """Delete an essay-writing session and its results."""
    db = read_db()
    db["essay_writing_sessions"].pop(session_id, None)
    db["essay_results"].pop(session_id, None)
    update_db(db)


#
# Program Analysis Flow (Features 2 & 3)
#
def create_program_analysis_session(
    user_id: str, university_list: List[str], criteria: List[str]
) -> str:
    """Start a new program-analysis session."""
    db = read_db()
    session_id = str(uuid.uuid4())
    db["program_analysis_sessions"][session_id] = {
        "user_id": user_id,
        "university_list": university_list,
        "comparison_criteria": criteria,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "status": "pending",
    }
    update_db(db)
    return session_id


def get_program_analysis_session(session_id: str) -> Dict[str, Any]:
    """Fetch a program-analysis session record."""
    db = read_db()
    if session_id not in db["program_analysis_sessions"]:
        raise KeyError(f"Analysis session {session_id} not found")
    return db["program_analysis_sessions"][session_id]


def save_raw_admissions_data(session_id: str, raw_data: Any) -> None:
    """Store scraped admissions data for a session."""
    db = read_db()
    if session_id not in db["program_analysis_sessions"]:
        raise KeyError(f"Analysis session {session_id} not found")
    db["raw_admissions_data"][session_id] = raw_data
    update_db(db)


def get_raw_admissions_data(session_id: str) -> Any:
    """Retrieve stored raw admissions data."""
    db = read_db()
    if session_id not in db["raw_admissions_data"]:
        raise KeyError(f"No raw data for session {session_id}")
    return db["raw_admissions_data"][session_id]


def save_structured_admissions_data(session_id: str, structured: Any) -> None:
    """Store processed admissions data for a session."""
    db = read_db()
    if session_id not in db["program_analysis_sessions"]:
        raise KeyError(f"Analysis session {session_id} not found")
    db["structured_admissions_data"][session_id] = structured
    update_db(db)


def get_structured_admissions_data(session_id: str) -> Any:
    """Retrieve stored structured admissions data."""
    db = read_db()
    if session_id not in db["structured_admissions_data"]:
        raise KeyError(f"No structured data for session {session_id}")
    return db["structured_admissions_data"][session_id]


def save_program_comparison_report(session_id: str, report: Any) -> None:
    """Store final comparison report for a session."""
    db = read_db()
    if session_id not in db["program_analysis_sessions"]:
        raise KeyError(f"Analysis session {session_id} not found")
    db["program_comparison_reports"][session_id] = report
    db["program_analysis_sessions"][session_id]["status"] = "completed"
    update_db(db)


def get_program_comparison_report(session_id: str) -> Any:
    """Retrieve stored program comparison report."""
    db = read_db()
    if session_id not in db["program_comparison_reports"]:
        raise KeyError(f"No comparison report for session {session_id}")
    return db["program_comparison_reports"][session_id]


def delete_program_analysis_session(session_id: str) -> None:
    """Delete a program-analysis session and its associated data."""
    db = read_db()
    db["program_analysis_sessions"].pop(session_id, None)
    db["raw_admissions_data"].pop(session_id, None)
    db["structured_admissions_data"].pop(session_id, None)
    db["program_comparison_reports"].pop(session_id, None)
    update_db(db)
