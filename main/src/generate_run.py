import json
import logging
from typing import Any, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import db as db
from crew import (
    cost_breakdown_crew,
    create_dynamic_checklist_crew,
    create_essay_writing_crew,
    create_program_analysis_crew,
    create_timeline_generator_crew,
    create_interview_prep_crew
)


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
                if task.agent.role == "University Info Scraper Agent":
                    raw_data = json.loads(raw) if _is_json(raw) else raw

                elif task.agent.role == "University Info Processor Agent":
                    structured = json.loads(raw) if _is_json(raw) else raw

                else:
                    report = {"comparison_report": raw}
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


def generate_application_planning_background(
    session_id: str,
    session_data: Dict[str, Any],
) -> None:
    flow = session_data.get("flow_type")
    logger.info(
        f"Starting application planning for session: {session_id}, flow: {flow}"
    )

    try:
        if flow == "dynamic_checklist":
            logger.info("Flow type is 'dynamic_checklist'")

            sess = db.get_checklist_session(session_id)
            sess["status"] = "in_progress"
            logger.info(f"Checklist session marked in progress: {sess}")
            all_db = db.read_db()
            all_db["checklist_sessions"][session_id] = sess
            db.update_db(all_db)

            result, tasks = create_dynamic_checklist_crew(
                session_id=session_id,
                nationality=session_data["nationality"],
                program_level=session_data["program_level"],
                university_list=session_data["university_list"],
            )
            logger.info("Checklist crew run complete")

            checklist = None
            for task in tasks:
                logger.debug(f"Evaluating task: {task.description}")
                desc = task.description.strip().lower()
                raw = task.output.raw
                if task.agent.role == "Dynamic Application Checklist Generator":
                    checklist = json.loads(raw) if _is_json(raw) else raw
                    logger.info(f"Checklist generated: {checklist}")
                    break

            db.save_dynamic_checklist(session_id, checklist)
            logger.info("Checklist saved to DB")

        elif flow == "cost_breakdown":
            logger.info("Flow type is 'cost_breakdown'")

            sess = db.get_cost_breakdown_session(session_id)
            sess["status"] = "in_progress"
            logger.info(f"Cost breakdown session marked in progress: {sess}")
            all_db = db.read_db()
            all_db["cost_breakdown_sessions"][session_id] = sess
            db.update_db(all_db)

            result, tasks = cost_breakdown_crew(
                session_id=session_id,
                university=session_data["university"],
                course=session_data["course"],
                applicant_type=session_data["applicant_type"],
                location=session_data["location"],
                preferences=session_data.get("preferences", ""),
            )
            logger.info("Cost breakdown crew run complete")

            breakdown = None
            for task in tasks:
                logger.debug(f"Evaluating task: {task.description}")
                desc = task.description.strip().lower()
                raw = task.output.raw
                if task.agent.role == "Cost Breakdown Generator":
                    breakdown = json.loads(raw) if _is_json(raw) else raw
                    logger.info(f"Breakdown generated: {breakdown}")
            db.save_cost_breakdown(session_id, breakdown)
            logger.info("Cost breakdown saved to DB")

        elif flow == "timeline":
            logger.info("Flow type is 'timeline'")

            sess = db.get_timeline_session(session_id)
            sess["status"] = "in_progress"
            logger.info(f"Timeline session marked in progress: {sess}")
            all_db = db.read_db()
            all_db["timeline_sessions"][session_id] = sess
            db.update_db(all_db)

            result, tasks = create_timeline_generator_crew(
                session_id=session_id,
                universities=session_data["universities"],
                level=session_data["level"],
                applicant_type=session_data["applicant_type"],
                nationality=session_data["nationality"],
                intake=session_data["intake"],
                applicant_availability=session_data.get("applicant_availability"),
            )
            logger.info("Timeline generator crew run complete")

            deadlines = None
            timeline = None
            for task in tasks:
                logger.debug(f"Evaluating task: {task.description}")
                desc = task.description.strip().lower()
                raw = task.output.raw
                if task.agent.role == "Deadline Extractor":
                    deadlines = json.loads(raw) if _is_json(raw) else raw
                    deadlines = deadlines.get("deadlines", {})
                    logger.info(f"Deadlines extracted: {deadlines}")
                elif task.agent.role == "Timeline Generator":
                    timeline = json.loads(raw) if _is_json(raw) else raw
                    logger.info(f"Timeline generated: {timeline}")

            db.save_timeline(session_id, deadlines, timeline)
            logger.info("Timeline data saved to DB")

        elif flow == "interview_prep":
            logger.info("Flow type is 'interview_prep'")
            sess = db.get_interview_prep_session(session_id)
            sess["status"] = "in_progress"
            all_db = db.read_db()
            all_db["interview_prep_sessions"][session_id] = sess
            db.update_db(all_db)

            result, tasks = create_interview_prep_crew(
                session_id=session_id,
                university_name=session_data["university_name"],
                course_name=session_data["course_name"],
                program_level=session_data["program_level"],
            )
            interview_QA = None
            for task in tasks:
                if task.agent.role == "Interview Preparation Generator":
                    raw = task.output.raw
                    interview_QA = json.loads(raw) if _is_json(raw) else raw
            db.save_interview_prep(session_id, interview_QA)
            logger.info("Interview preparation data saved to DB")
            
        else:
            raise ValueError(f"Unknown flow_type: {flow}")

    except Exception as e:
        logger.error(
            f"Error occurred during flow '{flow}' for session '{session_id}': {e}",
            exc_info=True,
        )
        if flow == "dynamic_checklist":
            sess = db.get_checklist_session(session_id)
            key = "checklist_sessions"
        elif flow == "cost_breakdown":
            sess = db.get_cost_breakdown_session(session_id)
            key = "cost_breakdown_sessions"
        elif flow == "timeline":
            sess = db.get_timeline_session(session_id)
            key = "timeline_sessions"
        elif flow == "interview_prep":
            sess = db.get_interview_prep_session(session_id)
            key = "interview_prep_sessions"
        else:
            raise

        sess["status"] = "failed"
        sess["error"] = str(e)
        d = db.read_db()
        d[key][session_id] = sess
        db.update_db(d)
        logger.info(f"Marked session {session_id} as failed and saved error")


def _is_json(s: str) -> bool:
    """Utility to detect whether a string can be parsed as JSON."""
    try:
        json.loads(s)
        return True
    except Exception:
        return False
