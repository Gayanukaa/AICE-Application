import os
import re
from crewai.tools import BaseTool, tool
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import AzureChatOpenAI
from pydantic import Field
from crewai_tools import (SerperDevTool, ScrapeWebsiteTool)

load_dotenv()


search = GoogleSerperAPIWrapper()


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

search_uni = SerperDevTool()
scrape_website = ScrapeWebsiteTool()

@tool("fetch_university_admission_info")
def fetch_university_admission_info(university_name: str, level: str, course: str, origin: str) -> dict:
    """
    Fetches raw admission-related information for a given university and program by querying and scraping relevant webpages.


    Args:
        university_name (str): Name of the target university.
        level (str): Level of study (e.g., "undergraduate", "postgraduate").
        course (str): Academic program or field (e.g., "computer science", "business").
        origin (str): Origin of the applicant (e.g., "international", "Sri Lankan").

    Returns:
        dict: A dictionary containing raw text data for each of the following keys:
            - "university": Name of the university.
            - "requirements": Scraped content for entry requirements.
            - "deadlines": Scraped content for application deadlines.
            - "fees": Scraped content for tuition fees.
            - "scholarships": Scraped content for scholarships and financial aid.
            - "university ranking": Scraped content for the university’s overall QS/world ranking.
            - "subject ranking": Scraped content for the course/subject's ranking.
            - "course structure": Scraped content for the curriculum or program structure.


    """
    fields = {
        "requirements": f"{university_name} {level} admission requirements for {course} for {origin} students.",
        "deadlines": f"{university_name} {level} application deadlines for {course} for {origin} students.",
        "fees": f"{university_name} {level} tuition fees for {course} for {origin} students.",
        "scholarships": f"{university_name} {level} scholarships and grants for {course} for {origin} students.",
        "university ranking": f"{university_name} latest qs ranking.",
        "subject ranking": f"latest qs ranking for {course} in at {university_name}.",
        "course structure": f"{university_name} latest {course}  curriculum structure."
    }


    results = {
        "University": university_name,
        "requirements": None,
        "deadlines": None,
        "fees": None,
        "scholarships": None,
        "university ranking": None,
        "subject ranking": None,
        "course structure": None

    }

    def extract_main_links(data):
        links = []
        for item in data.get('organic', []):
            if 'link' in item:
                links.append(item['link'])
        return links


    for field, query in fields.items():
        try:

            response = search_uni.run(search_query=query)
            urls = extract_main_links(response)         #Extract main links from response

            if not urls:
                results[field] = "No relevant URL found."
                continue

            url = urls[0]           #Select the first link


            if field == "course structure":
                scraped_content =  ScrapeWebsiteTool(website_url=url).run()
            else:
                scraped_content = ScrapeWebsiteTool(website_url=url).run()


            results[field] = (f"url: {url} \n" + scraped_content) or "Result not found."

        except Exception as e:
            results[field] = f"Error: {str(e)}"

    return results
