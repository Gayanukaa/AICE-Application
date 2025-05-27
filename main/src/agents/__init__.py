import os
from typing import Union

from crewai import LLM, Agent
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from tools import ( 
    SearchTool,
    # extract_relevant_content,
    file_read_tool,
    fetch_university_admission_info,
   
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
           "Accurately extract up-to-date admissions data based on {comparison_criteria} for each university listed in {university_list}," 
            "using web scraping and other credible data sources."
        ),
        backstory=(
            "You are a diligent and detail-oriented data acquisition specialist with expertise in web scraping." 
            "Your mission is to ensure that all retrieved admissions data is current, relevant, and comprehensive," 
            "forming the foundation for downstream processing and comparison."
        ),
        allow_delegation=False,
        llm=get_llm(uni_info_scraper_model, uni_info_scraper_temperature),
        tools=[fetch_university_admission_info ],
    )

    uni_info_processor_agent = Agent(
        role="University Info Processor Agent",
        goal=(
            "Extract and standardize the essential admissions data from {raw_data} based on the specified {comparison_criteria},"
            "and produce a final, clean representation of all relevant information."
            
        ),
        backstory=(
            "You are a focused and methodical data wrangler with expertise in extracting key insights from unstructured data."
            "Your role is to identify the most relevant information according to predefined comparison criteria,"
            "organize it into a consistent format, and deliver a final, clean dataset ready for analysis."
        ),
        
        allow_delegation=False,
        llm=get_llm(uni_info_processor_model, uni_info_processor_temperature),
        # tools=[extract_relevant_content],
    )

    program_comparison_agent = Agent(
        role="Program Comparison Agent",
        goal=(
            "Analyze and compare university programs using the provided {structured_data},"
            "and generate a detailed, user-friendly summary based on the specified {comparison_criteria}."
            "Use all available to tools to provide an answer"
            
        ),
        backstory=(
            "You are a detail-oriented academic program analyst with a strong foundation in comparative evaluation." 
            "Your responsibility is to interpret structured admissions data and translate it into clear," 
            "accessible insights that help users easily understand how programs differ and which options best match their needs."
        ),
        allow_delegation=False,
        llm=get_llm(program_comparison_model, program_comparison_temperature),
        tools=[file_read_tool],
    )

    return {
        "essay_brainstorm_agent": essay_brainstorm_agent,
        "essay_refinement_agent": essay_refinement_agent,
        "uni_info_scraper_agent": uni_info_scraper_agent,
        "uni_info_processor_agent": uni_info_processor_agent,
        "program_comparison_agent": program_comparison_agent,
    }