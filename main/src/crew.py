import os

from crewai import Crew, Process
from agents import create_college_exploration_agents
from tasks import create_college_exploration_tasks


def create_essay_writing_crew(
    session_id: str,
    essay_text: str,
    target_university: str,
    style_guidelines: str,
) -> tuple:
    """
    Create and run a Crew for the Essay Writing flow.

    This will invoke:
      1. essay_brainstorm_agent
      2. essay_refinement_agent
    """
    # prepare log directory
    log_dir = f"src/data/logs/{session_id}/essay"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "crew.log")

    # instantiate all agents, then pick only the essay ones
    agents = create_college_exploration_agents(session_id)
    selected_agents = {
        name: agents[name]
        for name in ("essay_brainstorm_agent", "essay_refinement_agent")
        if name in agents
    }

    # build only the essay‐writing tasks, now passing essay_text
    tasks = create_college_exploration_tasks(
        session_id=session_id,
        essay_text=essay_text,
        target_university=target_university,
        style_guidelines=style_guidelines,
        university_list=[],  # unused in this flow
        comparison_criteria=[],  # unused in this flow
        agents=selected_agents,
    )

    crew = Crew(
        agents=list(selected_agents.values()),
        tasks=list(tasks),
        verbose=True,
        Process=Process.sequential,
        output_log_file=log_file,
        full_output=True,
    )
    result = crew.kickoff()
    return result, tasks


def create_program_analysis_crew(
    session_id: str,
    university_list: list[str],
    comparison_criteria: list[str],
) -> tuple:
    """
    Create and run a Crew for Program Analysis flow (Features 2 & 3).

    This will invoke:
      1. uni_info_scraper_agent
      2. uni_info_processor_agent
      3. program_comparison_agent
    """
    # prepare log directory
    log_dir = f"src/data/logs/{session_id}/program_analysis"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "crew.log")

    # instantiate all agents, then pick only the program‐analysis ones
    agents = create_college_exploration_agents(session_id)
    selected_agents = {
        name: agents[name]
        for name in (
            "uni_info_scraper_agent",
            "uni_info_processor_agent",
            "program_comparison_agent",
        )
        if name in agents
    }

    # build only the program‐analysis tasks
    tasks = create_college_exploration_tasks(
        session_id=session_id,
        essay_text="",  # unused in this flow
        target_university="",  # unused in this flow
        style_guidelines="",  # unused in this flow
        university_list=university_list,
        comparison_criteria=comparison_criteria,
        agents=selected_agents,
    )

    crew = Crew(
        agents=list(selected_agents.values()),
        tasks=list(tasks),
        verbose=True,
        Process=Process.sequential,
        output_log_file=log_file,
        full_output=True,
    )
    result = crew.kickoff()
    return result, tasks
