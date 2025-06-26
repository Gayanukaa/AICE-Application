import os

import httpx
import nltk
from crewai import LLM
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain.schema import HumanMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI

load_dotenv()

nltk.download("vader_lexicon", quiet=True)


def get_llm_instance() -> AzureChatOpenAI | ChatOpenAI:
    """
    Instantiate an LLM. If USE_AZURE_OPENAI=true, use AzureChatOpenAI
    with the deployment name, endpoint, API version and key from env vars.
    Otherwise fall back to ChatOpenAI.
    """
    if os.getenv("USE_AZURE_OPENAI", "false").lower() == "true":
        return AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # type: ignore
            temperature=0.1,
        )
    else:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
        )


def construct_search_query(university: str, criterion: str) -> str:
    llm = get_llm_instance()

    prompt = f"""
    You are an expert in university search optimization.

    Turn the input below into a concise Google search query to find official university information.

    University: "{university}"
    Topic: "{criterion}"

    Use only course and degree names that are officially offered by this university.
    Do not guess or assume common names — include only terms that this university actually uses on its official website.

    Do NOT include:
    - URLs
    - search operators like site:
    - punctuation or quotation marks

    Return only the search query text.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def extract_essential_info(text: str, criteria: str) -> str:
    """
    Uses an LLM to extract only the essential information from the given text
    based on the specified criteria.

    Parameters:
    - text: str -> Raw text content scraped from a website.
    - criteria: str -> The specific information you want to extract (e.g. "entry requirements").

    Returns:
    - str -> The relevant extracted information.
    """
    llm = get_llm_instance()

    prompt = f"""
    You are a data extraction assistant. The following is raw text scraped from a website.
    Your task is to extract only the most relevant and essential content that matches the following criteria:

    Criteria: "{criteria}"

    Only return clean, readable, structured content. Remove any irrelevant information such as contact details, navigation menus, etc.

    Raw Text:
    \"\"\"{text}\"\"\"

    Extracted Information:
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()
