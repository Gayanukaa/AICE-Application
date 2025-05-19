import json
from typing import Any, Dict

import db as db
from crew import create_essay_writing_crew, create_program_analysis_crew


def generate_college_exploration_background(
    session_id: str,
    session_data: Dict[str, Any],
) -> None:
    """
    Dispatch the appropriate AICE flow based on session_data['flow_type']:
      - "essay"            → Essay Writing flow
      - "program_analysis" → Program Analysis flow (Features 2 & 3)
    Persist intermediate and final outputs into our JSON datastore.
    """
    flow = session_data.get("flow_type")
    try:
        if flow == "essay":
            # mark in-progress
            sess = db.get_essay_session(session_id)
            sess["status"] = "in_progress"
            all_db = db.read_db()
            all_db["essay_writing_sessions"][session_id] = sess
            db.update_db(all_db)

            # kickoff Essay Writing Crew, now using essay_text
            result, tasks = create_essay_writing_crew(
                session_id=session_id,
                essay_text=session_data["essay_text"],  # ← changed
                target_university=session_data["target_university"],
                style_guidelines=session_data["style_guidelines"],
            )

            # collect outputs
            outline = None
            refined = None
            for task in tasks:
                desc = task.description.strip().lower()
                raw = task.output.raw
                if "structure and outline" in desc:
                    outline = json.loads(raw) if _is_json(raw) else raw
                elif "refine" in desc:
                    refined = json.loads(raw) if _is_json(raw) else raw

            # save to DB (also marks session completed)
            db.save_essay_results(session_id, outline, refined)

        elif flow == "program_analysis":
            # unchanged…
            sess = db.get_program_analysis_session(session_id)
            sess["status"] = "in_progress"
            all_db = db.read_db()
            all_db["program_analysis_sessions"][session_id] = sess
            db.update_db(all_db)

            result, tasks = create_program_analysis_crew(
                session_id=session_id,
                university_list=session_data["university_list"],
                comparison_criteria=session_data["comparison_criteria"],
            )

            raw_data = None
            structured = None
            report = None
            for task in tasks:
                desc = task.description.strip().lower()
                raw = task.output.raw
                if "scrape admissions" in desc:
                    raw_data = json.loads(raw) if _is_json(raw) else raw
                elif "transform the raw" in desc or "structure" in desc:
                    structured = json.loads(raw) if _is_json(raw) else raw
                elif "compare" in desc:
                    report = json.loads(raw) if _is_json(raw) else raw
                elif task.agent.role == "Program Comparison Agent":
                    raw = task.output.raw
                    data = json.loads(raw) if _is_json(raw) else raw

                    if isinstance(data, dict) and "comparison_report" in data:
                        report = data["comparison_report"]
                    else:
                        report = data
                    break

            # save each stage
            db.save_raw_admissions_data(session_id, raw_data)
            db.save_structured_admissions_data(session_id, structured)
            db.save_program_comparison_report(session_id, report)

        else:
            raise ValueError(f"Unknown flow_type: {flow}")

    except Exception as e:
        # mark failed
        if flow == "essay":
            sess = db.get_essay_session(session_id)
            sess["status"] = "failed"
            sess["error"] = str(e)
            d = db.read_db()
            d["essay_writing_sessions"][session_id] = sess
            db.update_db(d)
        elif flow == "program_analysis":
            sess = db.get_program_analysis_session(session_id)
            sess["status"] = "failed"
            sess["error"] = str(e)
            d = db.read_db()
            d["program_analysis_sessions"][session_id] = sess
            db.update_db(d)
        else:
            # fallback for unrecognized flow
            raise


def _is_json(s: str) -> bool:
    """Utility to detect whether a string can be parsed as JSON."""
    try:
        json.loads(s)
        return True
    except Exception:
        return False
