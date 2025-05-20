import os
from typing import Union

from crewai import Agent, LLM
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from tools import (
    SearchTool,
#    compare_programs,
#    fetch_admissions_data,
#    process_admissions_data,
)
from utils import get_config_value, load_config

load_dotenv()


def create_college_exploration_agents(
    session_id: str,
) -> dict[str, Agent]:
    """Create agents for the AICE multi-agent system."""
    config = load_config()

    # Load model and temperature for each agent
    essay_brainstorm_model = get_config_value(config, "essay_brainstorm_agent", "model")
    essay_brainstorm_temperature = get_config_value(
        config, "essay_brainstorm_agent", "temperature"
    )

    essay_refinement_model = get_config_value(config, "essay_refinement_agent", "model")
    essay_refinement_temperature = get_config_value(
        config, "essay_refinement_agent", "temperature"
    )

    uni_info_scraper_model = get_config_value(config, "uni_info_scraper_agent", "model")
    uni_info_scraper_temperature = get_config_value(
        config, "uni_info_scraper_agent", "temperature"
    )

    uni_info_processor_model = get_config_value(
        config, "uni_info_processor_agent", "model"
    )
    uni_info_processor_temperature = get_config_value(
        config, "uni_info_processor_agent", "temperature"
    )

    program_comparison_model = get_config_value(
        config, "program_comparison_agent", "model"
    )
    program_comparison_temperature = get_config_value(
        config, "program_comparison_agent", "temperature"
    )

    def get_llm(model_name: str, temperature: float) -> Union[LLM, ChatOpenAI]:
        if os.getenv("USE_AZURE_OPENAI") == "true":
            return LLM(
                model=f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}",
                api_version=os.getenv("OPENAI_API_VERSION"),
                api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                temperature=temperature,
            )
        return ChatOpenAI(model=model_name, temperature=temperature)

    # -- Feature 1: Essay Writing Agents --

    # Agent: Structure and outline an uploaded essay
    essay_brainstorm_agent = Agent(
        system_template="""You are an expert academic writing coach.
        Always respond with valid JSON matching the schema:
        { "topics": [...], "outline": { section: [bullets] } }
        Do not add any prose outside the JSON.""",
        role="Essay Brainstorm Agent",
        goal=(
            "Structure and outline the uploaded essay text {essay_text} into a clear framework "
            "with introduction, body points, and conclusion aligned to {target_university} expectations."
        ),
        backstory=(
            "You are a creative assistant specialized in academic essay development, "
            "adept at analyzing draft essays and organizing them into structured outlines."
        ),
        allow_delegation=False,
        llm=get_llm(essay_brainstorm_model, essay_brainstorm_temperature),
        tools=[SearchTool()],
    )

    # Agent: Refine and polish the uploaded essay using provided outline
    essay_refinement_agent = Agent(
        role="Essay Refinement Agent",
        goal=(
            "Refine and polish the uploaded essay text {essay_text} using the outline and "
            "{style_guidelines}: correct grammar, improve tone, and enhance clarity."
            "First THINK through each section you will propose (in plain English, preceded by “THOUGHT: …”), then output the final JSON ONLY under a ###Final Answer### heading."
        ),
        backstory=(
            "You are an expert editor with a strong command of academic writing, "
            "known for improving clarity, coherence, and adherence to guidelines."
        ),
        allow_delegation=False,
        llm=get_llm(essay_refinement_model, essay_refinement_temperature),
        # tools=[],
    )

    # -- Features 2 & 3: Program Analysis Agents --

    uni_info_scraper_agent = Agent(
        role="University Info Scraper Agent",
        goal=(
            "Scrape admissions data (requirements, deadlines, fees, scholarships) "
            "for each university in {university_list}."
        ),
        backstory=(
            "You are a meticulous data collector skilled in web scraping and API integration, "
            "committed to gathering accurate and comprehensive admissions information."
        ),
        allow_delegation=False,
        llm=get_llm(uni_info_scraper_model, uni_info_scraper_temperature),
        # tools=[SearchTool(), fetch_admissions_data],
    )

    uni_info_processor_agent = Agent(
        role="University Info Processor Agent",
        goal=(
            "Transform raw admissions data {raw_data} into a consistent JSON schema "
            "with fields: requirements, deadlines, fees, scholarships."
        ),
        backstory=(
            "You are a data wrangler experienced in cleaning and structuring unstructured data, "
            "turning raw inputs into standardized formats."
        ),
        allow_delegation=False,
        llm=get_llm(uni_info_processor_model, uni_info_processor_temperature),
        # tools=[process_admissions_data],
    )

    program_comparison_agent = Agent(
        role="Program Comparison Agent",
        goal=(
            "Analyze structured data {structured_data} and compare programs "
            "using criteria {comparison_criteria} "
            "(e.g., cost, ranking, curriculum, funding)."
        ),
        backstory=(
            "You are an analytical consultant proficient in comparative analysis, "
            "capable of producing clear, insightful reports to assist decision-making."
        ),
        allow_delegation=False,
        llm=get_llm(program_comparison_model, program_comparison_temperature),
        # tools=[compare_programs],
    )

    return {
        "essay_brainstorm_agent": essay_brainstorm_agent,
        "essay_refinement_agent": essay_refinement_agent,
        "uni_info_scraper_agent": uni_info_scraper_agent,
        "uni_info_processor_agent": uni_info_processor_agent,
        "program_comparison_agent": program_comparison_agent
    }

def create_university_planning_agents(
    session_id: str,
) -> dict[str, Agent]:
    """Create agents for the AICE multi-agent system."""
    config = load_config()

    dynamic_checklist_model = get_config_value(
        config, "dynamic_checklist_agent", "model"
    )
    dynamic_checklist_temperature = get_config_value(
        config, "dynamic_checklist_agent", "temperature"
    )

    cost_breakdown_model = get_config_value(
        config, "cost_breakdown_agent", "model"
    )
    cost_breakdown_temperature = get_config_value(
        config, "cost_breakdown_agent", "temperature"
    )

    timeline_planner_model = get_config_value(
        config, "timeline_planner_agent", "model"
    )
    timeline_planner_temperature = get_config_value(
        config, "timeline_planner_agent", "temperature"
    )

    fee_retriever_model = get_config_value(
        config, "fee_retriever_agent", "model"
    )
    fee_retriever_temperature = get_config_value(
        config, "fee_retriever_agent", "temperature"
    )

    deadline_extractor_model = get_config_value(
        config, "deadline_extractor_agent", "model"
    )
    deadline_extractor_temperature = get_config_value(
        config, "deadline_extractor_agent", "temperature"
    )

    def get_llm(model_name: str, temperature: float) -> Union[LLM, ChatOpenAI]:
        if os.getenv("USE_AZURE_OPENAI") == "true":
            return LLM(
                model=f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}",
                api_version=os.getenv("OPENAI_API_VERSION"),
                api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                temperature=temperature,
            )
        return ChatOpenAI(model=model_name, temperature=temperature)

    dynamic_checklist_agent = Agent(
        role="Dynamic Application Checklist Generator",
        goal=(
            "Build a tailored document checklist for each university/course, "
            "considering the applicant’s nationality, program level, and specific university requirements."
        ),
        backstory=(
            "You are an expert admissions consultant with deep knowledge of global university "
            "application processes. You craft precise, customized checklists to ensure applicants "
            "never miss a required document."
        ),
        allow_delegation=False,
        llm=get_llm(dynamic_checklist_model, dynamic_checklist_temperature),
        # tools=[generate_checklist_tool],
    )

        # 1a. University Fee Retriever Agent
    '''
        university_name (or list of names)
        program_level (e.g. “Bachelor”, “Master”)
        (optional) year or academic session if fees vary by intake
    '''
    fee_retriever_agent = Agent(
        role="University Fee Retriever",
        goal=(
            "Fetch and aggregate tuition fees and any official university cost estimates "
            "for a given program level at a specific destination."
        ),
        backstory=(
            "You are a data-driven researcher with expertise scraping and normalizing university "
            "fee schedules worldwide."
        ),
        allow_delegation=False,
        llm=get_llm(fee_retriever_model, fee_retriever_temperature),
        # tools=[scrape_university_fees_tool],
    )
    '''
    user_budget (e.g. total or per-month)
    destination_country (or city)
    Plus output from University Fee Retriever, namely: "tuition_fee", "program_level", "university_name"
    (optional) any user preferences (e.g. “prefer on-campus housing”)
    '''
    # 1b. Cost Breakdown Generator Agent
    cost_breakdown_generator_agent = Agent(
        role="Cost Breakdown Generator",
        goal=(
            "Create a line-item financial plan covering tuition, accommodation, living expenses, "
            "visa/insurance costs, and travel/miscellaneous expenses, tailored to the user’s budget "
            "and destination."
        ),
        backstory=(
            "You are a seasoned financial planner for international students, adept at translating "
            "budgets and fee data into clear, actionable expense breakdowns."
        ),
        allow_delegation=False,
        llm=get_llm(cost_breakdown_model, cost_breakdown_temperature),
        # tools=[calculate_expenses_tool],
    )
    '''
    university_name
    program_level
    intake_term (e.g. “Fall 2026”)
    '''
    # 2a. Deadline Extractor Agent
    deadline_extractor_agent = Agent(
        role="Deadline Extractor",
        goal=(
            "Scrape and consolidate all relevant application deadlines—start/end dates, "
            "essay submission, interviews, scholarships—for a given university/program."
        ),
        backstory=(
            "You are a meticulous researcher who specializes in harvesting deadline data "
            "from university admission sites and official calendars."
        ),
        allow_delegation=False,
        llm=get_llm(deadline_extractor_model, deadline_extractor_temperature),
        # tools=[scrape_university_deadlines_tool],
    )
    '''
    Output from Deadline Extractor Agent: "application_start", "application_end",
    "essay_deadline", "interview_periods", "scholarship_deadlines"
    '''
    # 2b. Timeline Generator Agent
    timeline_generator_agent = Agent(
        role="Timeline Generator",
        goal=(
            "Build an interactive timeline that schedules all application tasks—essay drafts, "
            "document uploads, interviews, scholarships—and suggests optimal completion windows."
        ),
        backstory=(
            "You are a project‐management AI expert who turns a set of dates into a step‐by‐step "
            "action plan with buffer times and reminders."
        ),
        allow_delegation=False,
        llm=get_llm(timeline_planner_model, timeline_planner_temperature),
        # tools=[create_timeline_tool, send_reminders_tool],
    )


    return {
        "dynamic_checklist_agent": dynamic_checklist_agent,
        "fee_retriever_agent": fee_retriever_agent,
        "cost_breakdown_generator_agent": cost_breakdown_generator_agent,
        "deadline_extractor_agent": deadline_extractor_agent,
        "timeline_generator_agent": timeline_generator_agent
    }

