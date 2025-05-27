from typing import Any, Dict, List, Optional

from config.report_paths import (
    COST_BREAKDOWN_FILE,
    DEADLINES_FILE,
    DYNAMIC_CHECKLIST_FILE,
    ESSAY_OUTLINE_FILE,
    PROGRAM_COMPARISON_REPORT_FILE,
    RAW_ADMISSIONS_DATA_FILE,
    RAW_FEES_FILE,
    REFINED_ESSAY_FILE,
    STRUCTURED_ADMISSIONS_DATA_FILE,
    TIMELINE_FILE,
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


# --- University Planning Outputs ---


class ChecklistItem(BaseModel):
    document: str
    required: bool
    notes: Optional[str]


class Checklist(BaseModel):
    """Output model for dynamic application checklist."""

    university: str
    items: List[ChecklistItem]


class RawFees(BaseModel):
    """Output model for raw university fee retrieval."""

    university: str
    program_level: str
    tuition_fee: float


class CostItem(BaseModel):
    category: str
    cost: float


class CostBreakdown(BaseModel):
    """Output model for detailed cost estimation."""

    total_budget: float
    breakdown: List[CostItem]


class InterviewPeriod(BaseModel):
    start: str  # ISO date
    end: str  # ISO date


class DeadlineData(BaseModel):
    """Output model for extracted application deadlines."""

    university: str
    application_start: str
    application_end: str
    essay_deadline: Optional[str]
    interview_periods: List[InterviewPeriod]
    scholarship_deadlines: List[str]


class TimelineEvent(BaseModel):
    date: str
    task: str


class SuggestedItem(BaseModel):
    task: str
    recommended_date: str


class ApplicationTimeline(BaseModel):
    """Output model for suggested application timeline."""

    events: List[TimelineEvent]
    suggestions: List[SuggestedItem]


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
            Scrape admissions data for the following universities:
            {university_list}

            Gather:
            - Requirements
            - Deadlines
            - Fees
            - Scholarships
            """,
            expected_output="Raw JSON or HTML data for each university.",
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
            expected_output="Clean, structured admissions information as JSON.",
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
            expected_output="A comparison report summarizing key differences and recommendations.",
            agent=agents["program_comparison_agent"],
            output_file=_path(PROGRAM_COMPARISON_REPORT_FILE),
            output_json=ProgramComparisonReport,
            context=[ctx["process_admissions"]],
        )
        tasks.append(t5)
        ctx["compare_programs"] = t5

    return tasks


def create_university_planning_tasks(
    session_id: str,
    nationality: str,
    program_level: str,
    university_list: List[str],
    user_budget: float,
    destination: str,
    applicant_availability: Optional[str],
    agents: Dict[str, Agent],
) -> List[Task]:
    """Build tasks for checklist generation, cost planning, and timeline planning flows."""

    def _path(template: str) -> str:
        return template.format(session_id=session_id)

    tasks: List[Task] = []
    ctx: Dict[str, Task] = {}

    if "dynamic_checklist_agent" in agents:
        t1 = Task(
            description=f"""
            Build a tailored document checklist for each university/course
            considering the applicant’s nationality and program level:

            - Applicant nationality: {nationality}
            - Program level: {program_level}
            - Universities: {university_list}
            """,
            expected_output="""
            A JSON array of checklists, one per university, each item:
            - document: string
            - required: bool
            - notes: optional string
            """,
            agent=agents["dynamic_checklist_agent"],
            output_file=_path(DYNAMIC_CHECKLIST_FILE),
            output_json=Checklist,
        )
        tasks.append(t1)
        ctx["checklist"] = t1

    # --- Feature 5: Personalized Cost Breakdown ---

    # Task 2: Fetch raw university fee data
    if "fee_retriever_agent" in agents:
        t2 = Task(
            description=f"""
            Retrieve tuition fees for the following universities and program level:
            - Universities: {university_list}
            - Program level: {program_level}
            """,
            expected_output="""
            A JSON object per university:
            - university: string
            - program_level: string
            - tuition_fee: number
            """,
            agent=agents["fee_retriever_agent"],
            output_file=_path(RAW_FEES_FILE),
            output_json=RawFees,
        )
        tasks.append(t2)
        ctx["fees"] = t2

    # Task 3: Generate comprehensive cost breakdown
    if "cost_breakdown_generator_agent" in agents and "fees" in ctx:
        t3 = Task(
            description=f"""
            Create a detailed cost breakdown using:
            - User budget: {user_budget}
            - Destination: {destination}
            - Tuition fee data: {{{{steps.fees.output}}}}

            Include line items for:
            • Accommodation
            • Living expenses (food, transport, utilities)
            • Visa & insurance
            • Travel & misc.
            """,
            expected_output="""
            A JSON object:
            - total_budget: number
            - breakdown: list of { category: string, cost: number }
            """,
            agent=agents["cost_breakdown_generator_agent"],
            output_file=_path(COST_BREAKDOWN_FILE),
            output_json=CostBreakdown,
            context=[ctx["fees"]],
        )
        tasks.append(t3)
        ctx["costs"] = t3

    # --- Feature 6: Interactive Application Timeline Planner ---

    # Task 4: Extract all relevant deadlines
    if "deadline_extractor_agent" in agents:
        t4 = Task(
            description=f"""
            Scrape and consolidate application deadlines for:
            - Universities: {university_list}
            - Program level: {program_level}

            Extract:
            • Application start/end
            • Essay submission
            • Interview windows
            • Scholarship deadlines
            """,
            expected_output="""
            A JSON object:
            - application_start: date
            - application_end: date
            - essay_deadline: date
            - interview_periods: list of { start: date, end: date }
            - scholarship_deadlines: list of dates
            """,
            agent=agents["deadline_extractor_agent"],
            output_file=_path(DEADLINES_FILE),
            output_json=DeadlineData,
        )
        tasks.append(t4)
        ctx["deadlines"] = t4

    # Task 5: Generate the personalized timeline
    if "timeline_generator_agent" in agents and "deadlines" in ctx:
        t5 = Task(
            description=f"""
            Build an interactive application timeline using:
            - Extracted deadlines: {{{{steps.deadlines.output}}}}
            - Applicant availability preferences: {applicant_availability or "none"}

            Suggest optimal slots for:
            • Essay drafts & revisions
            • Document uploads
            • Interview prep
            • Scholarship applications
            """,
            expected_output="""
            A JSON timeline:
            - events: list of { date: date, task: string }
            - suggestions: list of { task: string, recommended_date: date }
            """,
            agent=agents["timeline_generator_agent"],
            output_file=_path(TIMELINE_FILE),
            output_json=ApplicationTimeline,
            context=[ctx["deadlines"]],
        )
        tasks.append(t5)
        ctx["timeline"] = t5

    return tasks
