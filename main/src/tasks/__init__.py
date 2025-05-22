from typing import Any, Dict, List

from config.report_paths import (
    ESSAY_OUTLINE_FILE,
    PROGRAM_COMPARISON_REPORT_FILE,
    RAW_ADMISSIONS_DATA_FILE,
    REFINED_ESSAY_FILE,
    STRUCTURED_ADMISSIONS_DATA_FILE,
)
from crewai import Agent, Task
from pydantic import BaseModel


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
    essay_text: str,
    target_university: str,
    style_guidelines: str,
    university_list: List[str],
    comparison_criteria: List[str],
    agents: Dict[str, Agent],
) -> List[Task]:
    """Build tasks for essay writing and program analysis flows."""

    def _path(template: str) -> str:
        return template.format(session_id=session_id)

    tasks: List[Task] = []
    ctx: Dict[str, Task] = {}

    # --- Feature 1: Essay Writing Flow ---

    # Task 1: Structure and outline the uploaded essay
    if "essay_brainstorm_agent" in agents:
        t1 = Task(
            description=f"""
            Structure and outline the uploaded essay text:

            {essay_text}

            Instructions:
            1. Identify introduction, key body points, and conclusion.
            2. Organize into a clear outline aligned with {target_university} expectations.
            """,
            expected_output="""
            A JSON object with:
            - topics: list of section headings or key themes.
            - outline: mapping of each section to bullet-point details.
            """,
            agent=agents["essay_brainstorm_agent"],
            output_file=_path(ESSAY_OUTLINE_FILE),
            output_json=EssayOutline,
        )
        tasks.append(t1)
        ctx["essay_brainstorm"] = t1

    # Task 2: Refine the uploaded essay using the outline and style guidelines
    if "essay_refinement_agent" in agents and "essay_brainstorm" in ctx:
        t2 = Task(
            description=f"""
            Refine the uploaded essay text using the outline from the previous task and style guidelines:

            **IMPORTANT** – Please put each outline section into its own paragraph, in order, separated by a blank line.

            Essay Text:
            {essay_text}

            Outline:
            {{{{steps.essay_brainstorm.outline}}}}

            Apply:
            1. Grammar, spelling, and punctuation correction.
            2. Tone and clarity enhancement.
            3. Alignment with university-specific expectations using {style_guidelines}.
            """,
            expected_output="""
            A JSON object with:
            - refined_draft: the polished essay text.
            """,
            agent=agents["essay_refinement_agent"],
            output_file=_path(REFINED_ESSAY_FILE),
            output_json=RefinedEssay,
            context=[ctx["essay_brainstorm"]],
        )
        tasks.append(t2)
        ctx["essay_refinement"] = t2

    # --- Features 2 & 3: Program Analysis Flow ---

    # Task 3: Scrape raw admissions data
    if "uni_info_scraper_agent" in agents:
        t3 = Task(
            description=f"""
            Scrape admissions data from the following universities:
            {university_list}

            Collect detailed information based on the following criteria:
            {comparison_criteria}
            """,
            expected_output="JSON containing raw scraped data for each university.",
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
            Process the raw admissions data obtained from the previous task and extract all relevant information 
            according to the specified comparison criteria. Transform this data into a clean, well-structured data.
            """,
            expected_output="Clean, structured JSON containing all admissions information based on the comparison criteria.",
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
            Compare the university programs using the structured admissions data,
            focusing on the following criteria:
            - Comparison Criteria: {comparison_criteria}
            """,
            expected_output="A user-friendly summary report highlighting the key differences between the programs. Give the output in a markdown schema",
            agent=agents["program_comparison_agent"],
            output_file=_path(PROGRAM_COMPARISON_REPORT_FILE),
            output_json=ProgramComparisonReport,
            context=[ctx["process_admissions"]],
        )
        tasks.append(t5)
        ctx["compare_programs"] = t5

    return tasks