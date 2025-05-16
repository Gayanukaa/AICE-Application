from typing import Dict, Any, List
from crewai import Agent, Task
from pydantic import BaseModel

from src.config.report_paths import (
    ESSAY_OUTLINE_FILE,
    REFINED_ESSAY_FILE,
    RAW_ADMISSIONS_DATA_FILE,
    STRUCTURED_ADMISSIONS_DATA_FILE,
    PROGRAM_COMPARISON_REPORT_FILE,
)


class EssayOutline(BaseModel):
    """Output model for essay brainstorming."""
    topics: List[str]
    outline: Dict[str, List[str]]


class RefinedEssay(BaseModel):
    """Output model for refined essay."""
    refined_draft: str


class RawAdmissionsData(BaseModel):
    """Output model for raw scraped admissions data."""
    raw_data: Any


class StructuredAdmissionsData(BaseModel):
    """Output model for cleaned admissions data."""
    structured_data: Any


class ProgramComparisonReport(BaseModel):
    """Output model for program comparison."""
    comparison_report: Any


def create_college_exploration_tasks(
    session_id: str,
    student_profile: str,
    target_university: str,
    style_guidelines: str,
    university_list: List[str],
    comparison_criteria: List[str],
    agents: Dict[str, Agent],
) -> List[Task]:
    """Build the list of Tasks for AICE flows: essay writing and program analysis."""

    def _path(template: str) -> str:
        return template.format(session_id=session_id)

    tasks: List[Task] = []
    ctx: Dict[str, Task] = {}

    # Task 1: Brainstorm essay topics & outline
    if "essay_brainstorm_agent" in agents:
        t1 = Task(
            description=f"""
            Generate personalized essay topic ideas and a high-level outline for:
            - Student Profile: {student_profile}
            - Target University: {target_university}

            Instructions:
            1. Brainstorm 5–10 essay topics.
            2. Create a structured outline covering introduction, body points, and conclusion.
            """,
            expected_output="""
            A JSON object containing:
            1. A list of essay topics (strings).
            2. An outline mapping each section to bullet points.
            """,
            agent=agents["essay_brainstorm_agent"],
            output_file=_path(ESSAY_OUTLINE_FILE),
            output_json=EssayOutline,
        )
        tasks.append(t1)
        ctx["essay_brainstorm"] = t1

    # Task 2: Refine outline into polished draft
    if "essay_refinement_agent" in agents and "essay_brainstorm" in ctx:
        t2 = Task(
            description=f"""
            Refine the essay based on the outline from the previous task:
            - Style Guidelines: {style_guidelines}

            Apply:
            1. Grammar and spelling correction.
            2. Tone and clarity enhancement.
            3. Alignment with specified style guidelines.
            """,
            expected_output="""
            A JSON object containing:
            1. The refined essay text as a single string.
            """,
            agent=agents["essay_refinement_agent"],
            output_file=_path(REFINED_ESSAY_FILE),
            output_json=RefinedEssay,
            context=[ctx["essay_brainstorm"]],
        )
        tasks.append(t2)
        ctx["essay_refinement"] = t2

    # Task 3: Scrape raw admissions data
    if "uni_info_scraper_agent" in agents:
        t3 = Task(
            description=f"""
            Scrape admissions data for the following universities:
            {university_list}

            Gather:
            - Requirements
            - Deadlines
            - Fees
            - Scholarships
            """,
            expected_output="""
            Raw JSON or HTML data for each university.
            """,
            agent=agents["uni_info_scraper_agent"],
            output_file=_path(RAW_ADMISSIONS_DATA_FILE),
            output_json=RawAdmissionsData,
        )
        tasks.append(t3)
        ctx["scrape_admissions"] = t3

    # Task 4: Structure admissions data
    if "uni_info_processor_agent" in agents and "scrape_admissions" in ctx:
        t4 = Task(
            description="""
            Transform the raw admissions data from the previous task into a clean JSON schema
            with fields: requirements, deadlines, fees, scholarships.
            """,
            expected_output="""
            Clean, structured admissions information as JSON.
            """,
            agent=agents["uni_info_processor_agent"],
            output_file=_path(STRUCTURED_ADMISSIONS_DATA_FILE),
            output_json=StructuredAdmissionsData,
            context=[ctx["scrape_admissions"]],
        )
        tasks.append(t4)
        ctx["process_admissions"] = t4

    # Task 5: Compare programs
    if "program_comparison_agent" in agents and "process_admissions" in ctx:
        t5 = Task(
            description=f"""
            Compare the programs using the structured admissions data:
            - Comparison Criteria: {comparison_criteria}

            Analyze differences in:
            • Cost
            • Ranking
            • Curriculum structure
            • Funding opportunities
            """,
            expected_output="""
            A comparison report (JSON or markdown) summarizing key differences
            and recommendations.
            """,
            agent=agents["program_comparison_agent"],
            output_file=_path(PROGRAM_COMPARISON_REPORT_FILE),
            output_json=ProgramComparisonReport,
            context=[ctx["process_admissions"]],
        )
        tasks.append(t5)
        ctx["compare_programs"] = t5

    return tasks
