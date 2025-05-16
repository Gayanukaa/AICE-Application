import os
from typing import Union

from crewai import Agent
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from src.tools import (
    SearchTool,
    fetch_admissions_data,
    process_admissions_data,
    compare_programs,
)
from src.utils import get_config_value, load_config

load_dotenv()


def create_college_exploration_agents(
    session_id: str,
) -> dict[str, Agent]:
    """Create agents for the AICE multi-agent system."""
    config = load_config()

    # Load model and temperature settings for each agent
    essay_brainstorm_model = get_config_value(
        config, "essay_brainstorm_agent", "model"
    )
    essay_brainstorm_temperature = get_config_value(
        config, "essay_brainstorm_agent", "temperature"
    )

    essay_refinement_model = get_config_value(
        config, "essay_refinement_agent", "model"
    )
    essay_refinement_temperature = get_config_value(
        config, "essay_refinement_agent", "temperature"
    )

    uni_info_scraper_model = get_config_value(
        config, "uni_info_scraper_agent", "model"
    )
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

    def get_llm(
        model_name: str, temperature: float
    ) -> Union[AzureChatOpenAI, ChatOpenAI]:
        """Instantiate an LLM based on environment and settings."""
        if os.getenv("USE_AZURE_OPENAI") == "true":
            azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("OPENAI_API_VERSION")
            return AzureChatOpenAI(
                model_name=model_name,
                azure_deployment=azure_deployment,
                api_version=api_version,
                api_key=api_key,
                temperature=temperature,
            )
        else:
            return ChatOpenAI(model=model_name, temperature=temperature)

    # Agent: Brainstorm essay topics and outline
    essay_brainstorm_agent = Agent(
        role="Essay Brainstorm Agent",
        goal=(
            "Generate personalized essay topic ideas and a high-level outline "
            "for {student_profile} targeting {target_university}."
        ),
        backstory=(
            "You are a creative assistant specialized in academic essay development, "
            "adept at understanding student backgrounds and tailoring topics to "
            "highlight their strengths and align with university requirements."
        ),
        allow_delegation=False,
        llm=get_llm(essay_brainstorm_model, essay_brainstorm_temperature),
        tools=[SearchTool()],
    )

    # Agent: Refine and polish the draft
    essay_refinement_agent = Agent(
        role="Essay Refinement Agent",
        goal=(
            "Refine and polish the essay draft {draft_text} by correcting grammar, "
            "improving tone, and ensuring alignment with {style_guidelines}."
        ),
        backstory=(
            "You are an expert editor with a strong command of academic writing, "
            "known for enhancing clarity, coherence, and adherence to target style guides."
        ),
        allow_delegation=False,
        llm=get_llm(essay_refinement_model, essay_refinement_temperature),
        tools=[],
    )

    # Agent: Scrape university admissions data
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
        tools=[SearchTool(), fetch_admissions_data],
    )

    # Agent: Process raw admissions data into a structured schema
    uni_info_processor_agent = Agent(
        role="University Info Processor Agent",
        goal=(
            "Transform raw admissions data {raw_data} into a consistent JSON schema "
            "with fields: requirements, deadlines, fees, scholarships."
        ),
        backstory=(
            "You are a data wrangler experienced in cleaning and structuring unstructured data, "
            "turning raw inputs into standardized, machine-readable formats."
        ),
        allow_delegation=False,
        llm=get_llm(uni_info_processor_model, uni_info_processor_temperature),
        tools=[process_admissions_data],
    )

    # Agent: Compare university programs side-by-side
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
        tools=[compare_programs],
    )

    return {
        "essay_brainstorm_agent": essay_brainstorm_agent,
        "essay_refinement_agent": essay_refinement_agent,
        "uni_info_scraper_agent": uni_info_scraper_agent,
        "uni_info_processor_agent": uni_info_processor_agent,
        "program_comparison_agent": program_comparison_agent,
    }
