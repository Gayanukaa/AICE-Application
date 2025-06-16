import os
from typing import List, Tuple

from agents import create_college_exploration_agents, create_university_planning_agents
from crewai import Crew, Process
from tasks import create_college_exploration_tasks, create_university_planning_tasks


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
    log_dir = f"data/logs/{session_id}/essay"
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
    log_dir = f"data/logs/{session_id}/program_analysis"
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


def create_dynamic_checklist_crew(
    session_id: str,
    nationality: str,
    program_level: str,
    university_list: List[str],
) -> Tuple:
    """
    Create and run a Crew for the Dynamic Application Checklist flow (Feature 4).

    This will invoke:
      1. dynamic_checklist_agent
    """
    # prepare log directory
    log_dir = f"data/logs/{session_id}/checklist"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "crew.log")

    # instantiate all planning agents, then pick only the checklist one
    agents = create_university_planning_agents(session_id)
    selected_agents = {
        name: agents[name] for name in ("dynamic_checklist_agent",) if name in agents
    }

    # build only the checklist tasks
    tasks = create_university_planning_tasks(
        session_id=session_id,
        universities=university_list,      
        university="",                  
        course="",                       
        level=program_level,             
        applicant_type="",              
        nationality=nationality,        
        intake="",                       
        applicant_availability="",       
        location="",                     
        preferences="",                  
        agents=selected_agents,
    )

    crew = Crew(
        agents=list(selected_agents.values()),
        tasks=tasks,
        verbose=True,
        Process=Process.sequential,
        output_log_file=log_file,
        full_output=True,
    )
    result = crew.kickoff()
    return result, tasks


def cost_breakdown_crew(
    session_id: str,
    university: str,
    course: str,
    applicant_type: str,
    location: str,
    preferences: str,
) -> Tuple:
    """
    Create and run a Crew for the Personalized Cost Breakdown flow (Feature 5).

    This will invoke:
      1. fee_retriever_agent
      2. cost_breakdown_generator_agent
    """
    # prepare log directory
    log_dir = f"data/logs/{session_id}/cost_breakdown"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "crew.log")

    # instantiate all planning agents, then pick only the cost ones
    agents = create_university_planning_agents(session_id)
    selected_agents = {
        name: agents[name]
        for name in ("fee_retriever_agent", "cost_breakdown_generator_agent")
        if name in agents
    }

    # build only the cost-breakdown tasks
    tasks = create_university_planning_tasks(
        session_id=session_id,
        universities=[],
        university=university,
        course=course,
        level="",
        applicant_type=applicant_type,
        nationality="",
        intake="",
        applicant_availability="",
        location=location,
        preferences=preferences,
        agents=selected_agents,
    )

    crew = Crew(
        agents=list(selected_agents.values()),
        tasks=tasks,
        verbose=True,
        Process=Process.sequential,
        output_log_file=log_file,
        full_output=True,
    )
    result = crew.kickoff()
    return result, tasks



def create_timeline_generator_crew(
    session_id: str,
    universities: list,
    level: str,
    applicant_type: str,
    nationality: str,
    intake: str,
    applicant_availability: str = None,
) -> Tuple:
    """
    Create and run a Crew for the Interactive Application Timeline flow (Feature 6).

    This will invoke:
      1. deadline_extractor_agent
      2. timeline_generator_agent
    """
    # prepare log directory
    log_dir = f"data/logs/{session_id}/timeline_planner"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "crew.log")

    # instantiate all planning agents, then pick only the timeline ones
    agents = create_university_planning_agents(session_id)
    selected_agents = {
        name: agents[name]
        for name in ("deadline_extractor_agent", "timeline_generator_agent")
        if name in agents
    }

    tasks = create_university_planning_tasks(
        session_id=session_id,
        universities=universities,
        university="",
        course="",
        level=level,
        applicant_type=applicant_type,
        nationality=nationality,
        intake = intake,
        applicant_availability=applicant_availability,
        location="",
        preferences="",
        agents=selected_agents,
    )
    crew = Crew(
        agents=list(selected_agents.values()),
        tasks=tasks,
        verbose=True,
        Process=Process.sequential,
        output_log_file=log_file,
        full_output=True,
    )
    result = crew.kickoff()
    return result, tasks