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
        "program_comparison_agent": program_comparison_agent,
    }
