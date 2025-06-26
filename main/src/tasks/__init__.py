import time
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


class ChecklistGroup(BaseModel):
    checklists: List[Checklist]


class RawFees(BaseModel):
    """Output model for raw university fee retrieval."""

    university: str
    course: str
    applicant_type: str
    tuition_fee: float
    other_fees: Dict[str, float]


class ExpenseDetail(BaseModel):
    amount: int
    description: str


class CostBreakdown(BaseModel):
    """Output model for detailed cost estimation."""

    currency: str
    expenses: Dict[str, ExpenseDetail]
    total_cost: int


class InterviewPeriod(BaseModel):
    start: str  # ISO date
    end: str  # ISO date


class Uni_DeadlineData(BaseModel):
    """Output model for extracted application deadlines."""

    university: str
    application_start: str
    application_end: str
    essay_deadline: Optional[str]
    interview_periods: List[InterviewPeriod]
    scholarship_deadlines: List[str]


class DeadlineData(BaseModel):
    """Top-level container for university deadline data."""

    deadlines: List[Uni_DeadlineData]


class TimelineEvent(BaseModel):
    date: str
    task: str


class SuggestedItem(BaseModel):
    task: str
    recommended_date: str


class DeadlineEvent(BaseModel):

    date: str
    name: str


class ApplicationTimeline(BaseModel):
    """Output model for suggested application timeline."""

    deadlines: List[DeadlineEvent]
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

            1. Alignment with university-specific expectations using {style_guidelines}.
            2. Grammar, spelling, and punctuation correction.
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

            If suitable information for the {comparison_criteria} is not available, indicate that the data could not be found.
            """,
            expected_output="A user-friendly summary report highlighting the key differences between the programs. Present the output according to the specified markdown format in the comp_instructions.md file",
            agent=agents["program_comparison_agent"],
            output_file=_path(PROGRAM_COMPARISON_REPORT_FILE),
            # output_json=ProgramComparisonReport,
            context=[ctx["process_admissions"]],
        )
        tasks.append(t5)
        ctx["compare_programs"] = t5

    return tasks


def create_university_planning_tasks(
    session_id: str,
    universities: list,
    university: str,
    course: str,
    level: str,
    applicant_type: str,
    nationality: str,
    intake: str,
    applicant_availability: Optional[str],
    location: str,
    preferences: str,
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
            - Program level: {level}
            - Universities: {universities}
            """,
            expected_output="""
            JSON object with a key 'checklists' (list), where each item contains:
            - university (str)
            - items (list of):
            - document (str)
            - required (bool)
            - notes (optional str)
            """,
            agent=agents["dynamic_checklist_agent"],
            output_file=_path(DYNAMIC_CHECKLIST_FILE),
            output_json=ChecklistGroup,
        )
        tasks.append(t1)
        ctx["checklist"] = t1

    # --- Feature 5: Personalized Cost Breakdown ---

    # Task 2: Fetch raw university fee data
    if "fee_retriever_agent" in agents:
        t2 = Task(
            description=f"""
            Retrieve and standardize tuition fee and cost-of-attendance data as of {time.localtime().tm_year} for the specified program:
            - University: {university}
            - Course: {course}
            - Applicant type: {applicant_type}

            Ensure the data is accurate, up to date, clearly structured, and reflects the most recent official figures.
            """,
            expected_output="""
             A JSON object with the following structure:
            -university: string,
            -course: string,
            -applicant type: string,
            -tuition fee: float,
            -other fees: {
                    <fee type>: float,
                    ...
                    }
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
            Using the tuition fee data and user context, generate a detailed annual cost breakdown for studying at the given university based on the following:
            - Applicant type: {applicant_type}
            - Location: {location}
            - Relevant preferences: {preferences}
            - Tuition and other fees: {{{{steps.fees.output}}}}

            Breakdown must include:
            • Tuition fees
            • Accommodation
            • Living expenses (food, utilities)
            • Visa and insurance
            • Travel expenses
            • Other fees(if present)

            Estimate each item based on location,applicant type and preferences where applicable.
            Include the used currency for the breakdown.
            """,
            expected_output="""
            A JSON object:
            -currency: string
            -expenses: {
                "<expense category>": {
                    "amount": integer,
                    "description": string (A detailed paragraph explaining the expense and how the amount was calculated.),
                    },
                    ...
                },
            -total_cost: integer
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
            As of {time.strftime("%Y-%m-%d")}, scrape and consolidate application deadlines for:
            - Universities: {universities}
            - Program level: {level}
            - Target intake period: {intake}

            Extract the following date information:
            • Application start and end dates
            • Essay submission deadline
            • Interview periods (with start and end)
            • Scholarship application deadlines



            """,
            expected_output=f"""
                A JSON object:
                - deadlines: a list of objects, each containing:
                    - university: string
                    - application_start: date
                    - application_end: date
                    - essay_deadline: date
                    - interview_periods: list of objects with:
                        - start: date
                        - end: date
                    - scholarship_deadlines: list of dates

                NOTE: If no data is available, return an empty string or list accordingly.

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
            As of {time.strftime("%Y-%m-%d")}, build a personalized application timeline using:
            - Extracted deadlines: {{{{steps.deadlines.output}}}}
            - Applicant's availability preferences: {applicant_availability}
            - Target intake period: {intake}

            The timeline should propose optimal time slots for:
            • Writing and revising essays
            • Uploading supporting documents
            • Preparing for interviews
            • Applying for scholarships

            IMPORTANT:
            - Timeline must not include dates prior to {time.strftime("%Y-%m-%d")}.

            Note: If all extracted deadlines are earlier than today ({time.strftime("%Y-%m-%d")}),
                  return empty lists for deadlines, events, and suggestions.

            Include each university’s key dates only in the deadlines:
            application start and end dates, essay submission deadline, interview periods, and scholarship application deadlines.

            """,
            expected_output="""
            A JSON timeline:
            - deadlines: list of { date: date, name: string}
            - events: list of { date: date, task: string}
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
