import os
import re

from typing import List, Dict
from crewai.tools import BaseTool, tool
from crewai_tools import FileReadTool, ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import AzureChatOpenAI
from pydantic import Field
from utils.program_analysis_utils import extract_essential_info, construct_search_query

load_dotenv()


search = GoogleSerperAPIWrapper(serper_api_key=os.getenv("SERPER_API_KEY"))


class SearchTool(BaseTool):
    name: str = "Search"
    description: str = (
        "Useful for search-based queries. Use this to find current information about markets, companies, and trends."
    )
    search: GoogleSerperAPIWrapper = Field(default_factory=GoogleSerperAPIWrapper)

    def _run(self, query: str) -> str:
        """Execute the search query and return results"""
        try:
            return self.search.run(query)
        except Exception as e:
            return f"Error performing search: {str(e)}"


file_read_tool = FileReadTool()
search_uni = SerperDevTool()


class UniversitySearchTool(BaseTool):
    name: str = "UniversitySearch"
    description: str = (
        "Searches for information about a university based on multiple criteria. "
        "For curriculum or course structure-related queries, it scrapes the university's website."
    )
    search: GoogleSerperAPIWrapper = Field(default_factory=lambda: GoogleSerperAPIWrapper(serper_api_key=os.getenv("SERPER_API_KEY")))

    def _is_course_related(self, criterion: str) -> bool:
        keywords = ['course', 'curriculum', 'syllabus', 'subjects', 'modules', 'program', 'structure']
        return any(keyword in criterion.lower() for keyword in keywords)

    def _scrape_site(self, url: str) -> str:
        try:
            return ScrapeWebsiteTool(website_url=url).run()
        except Exception as e:
            return f"Error scraping website: {str(e)}"

    def _search_url(self, query: str) -> str:
        # Extract the top URL from a search query
        try:
            url = extract_main_links(search_uni.run(search_query=query))[0]
            return url
        except Exception:
            return ""

    def _run(self, university: str, criteria: List[str]) -> Dict[str, str]:
        """
        Searches for information about a university based on given criteria.

        If a criterion is course-related, it scrapes data from a relevant URL.
        Otherwise, it performs a normal search.

        Returns a dictionary with each criterion and its result.
        """

        result = {}
        for criterion in criteria:
            query = construct_search_query(university, criterion)
            if self._is_course_related(criterion):
                url = self._search_url(query)
                if url:
                    content = self._scrape_site(url)
                    result[criterion] = extract_essential_info(content, query)
                else:
                    result[criterion] = "No relevant URL found for scraping."

            else:
                try:
                    content = self.search.run(query)
                    result[criterion] = content
                except Exception as e:
                    result[criterion] = f"Error performing search: {str(e)}"
        return result


def extract_main_links(data):
    links = []
    for item in data.get("organic", []):
        if "link" in item:
            links.append(item["link"])
    return links


@tool("read_comparison_instructions")
def read_comparison_instructions() -> str:
    """
    Loads a markdown file containing guidelines for comparing universities
    and formatting the information in markdown.

    Returns:
        str: Markdown-formatted instructions for university comparison.
    """
    instructions = file_read_tool._run(file_path="tools/comp_instructions.md")
    return instructions


@tool("fetch_university_admission_info")
def fetch_university_admission_info(
    university_name: str, field: str, level: str, course: str
) -> str:
    """
    Retrieves specific admission-related information for a given university and level of study
    by scraping university websites.

    Args:
        university_name (str): Name of the university to retrieve information from.
        field (str): The specific admission-related detail to retrieve.
                     Possible values include:
                        - "entry requirements"
                        - "admission deadlines"
                        - "tution fees/cost"
                        - "scholarships/grants"
                        - "university ranking"
                        - "subject ranking"
                        - "course curriculum"
                        - "duration"
        level (str): Level of study (e.g., "undergraduate", "postgraduate").
        course (str): Name of subject course/program

    Returns:
        dict: Extracted information and source URL for the requested field.
              Format: { field: {"url": str or None, "content": str} }
    """

    try:
        result = "No results found"
        search_query = f"{field} for {level} {course} at {university_name}"
        response = search_uni.run(search_query=search_query)
        urls = extract_main_links(response)
        url = urls[0]
        if url:
            content = ScrapeWebsiteTool(website_url=url).run()
            result = f"url: {url}\n" + content

    except Exception as e:
        result = f"Error: {str(e)}"

    return result


@tool("fetch_university_fees")
def fetch_university_fees(
    university: str, course: str, origin: str, level: str
) -> dict:
    """
    Retrieves tuition fee and miscellaneous expense information for a given university program
    by scraping relevant university websites.

    Args:
        university (str): Name of the university offering the program.
        course (str): Name of the course or program of interest.
        origin (str): The applicant's country or residency status (e.g., "international", "domestic").
        level (str): Level of study (e.g., "undergraduate", "postgraduate").

    Returns:
        dict: A dictionary containing:
            - "tuition_fees": A dictionary with:
                - "url": The URL of the page from which tuition fee data was scraped.
                - "content": The raw text containing tuition fee information.
            - "miscellaneous_expenses": A dictionary with:
                - "url": The URL of the page from which miscellaneous expense data was scraped.
                - "content": The raw text containing miscellaneous expense information.
    """

    result = {
        "tuition_fees": {"url": None, "content": "No results found"},
        "miscellaneous_expenses": {"url": None, "content": "No results found"},
    }

    try:
        tuition_fee_query = (
            f"{university} {level} {course} {origin} student tuition fees"
        )
        miscellaneous_expenses_query = f"{university} miscellaneous expenses"

        tf_url = extract_main_links(search_uni.run(search_query=tuition_fee_query))[0]
        me_url = extract_main_links(
            search_uni.run(search_query=miscellaneous_expenses_query)
        )[0]

        if tf_url:
            result["tuition_fees"]["url"] = tf_url
            result["tuition_fees"]["content"] = ScrapeWebsiteTool(
                website_url=tf_url
            ).run()

        if me_url:
            result["miscellaneous_expenses"]["url"] = me_url
            result["miscellaneous_expenses"]["content"] = ScrapeWebsiteTool(
                website_url=me_url
            ).run()

        return result["miscellaneous_expenses"]

    except Exception as e:
        return {"error": str(e)}


@tool("fetch_university_deadlines")
def fetch_university_deadlines(university: str, origin: str, level: str) -> dict:
    """
    Fetches application and scholarship deadline information for a specific university program
    based on the applicant's origin and level of study. Performs a web search to locate relevant
    university pages and scrapes them for deadline data.

    Args:
        university (str): Name of the university offering the program.
        origin (str): The applicant's country or residency status (e.g., "international", "domestic").
        level (str): Level of study (e.g., "undergraduate", "postgraduate").

    Returns:
        dict: A dictionary containing:
            - "University deadlines": {
                "url": URL of the page with application deadline info,
                "content": Raw text content extracted from the page
              }
            - "Scholarship deadlines": {
                "url": URL of the page with scholarship deadline info,
                "content": Raw text content extracted from the page
              }
    """
    result = {
        "University deadlines": {"url": None, "content": "No results found"},
        "Scholarship deadlines": {"url": None, "content": "No results found"},
    }

    try:
        university_deadlines_query = (
            f"{university} {origin} prospective {level} student application deadlines"
        )
        scholarships_deadlines_query = (
            f"{university} {origin} prospective {level} student scholarship deadlines"
        )

        ud_url = extract_main_links(
            search_uni.run(search_query=university_deadlines_query)
        )[0]
        sd_url = extract_main_links(
            search_uni.run(search_query=scholarships_deadlines_query)
        )[0]

        if ud_url:
            result["University deadlines"]["url"] = ud_url
            result["University deadlines"]["content"] = ScrapeWebsiteTool(
                website_url=ud_url
            ).run()

        if ud_url:
            result["Scholarship deadlines"]["url"] = ud_url
            result["Scholarship deadlines"]["content"] = ScrapeWebsiteTool(
                website_url=sd_url
            ).run()

        return result

    except Exception as e:
        return {"error": str(e)}

