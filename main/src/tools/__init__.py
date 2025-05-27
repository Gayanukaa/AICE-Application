import os
import re

from crewai.tools import BaseTool, tool
from crewai_tools import FileReadTool, ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import AzureChatOpenAI
from pydantic import Field

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


file_read_tool = FileReadTool(file_path="./main/src/tools/Comp_Instructions.md")
search_uni = SerperDevTool()
scrape_website = ScrapeWebsiteTool()


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
                        - "fees/cost"
                        - "scholarships/grants"
                        - "university ranking"
                        - "subject ranking"
                        - "course curriculum"
                    Use synonyms when necessary
        level (str): Level of study (e.g., "undergraduate", "postgraduate").
        course (str): Name of subject course/program

    Returns:
        str: Extracted information related to the requested field for the given university and level of study.
    """

    def extract_main_links(data):
        links = []
        for item in data.get("organic", []):
            if "link" in item:
                links.append(item["link"])
        return links

    try:
        response = search_uni.run(
            search_query=f"{field} for {level} {course} at {university_name} "
        )
        urls = extract_main_links(response)  # Extract main links from response

        if not urls:
            result = "No relevant URL found."

        url = urls[0]  # Select the first link

        result = ScrapeWebsiteTool(website_url=url).run()

    except Exception as e:
        result = f"Error: {str(e)}"

    return result


# @tool("extract_relavant_content")
# def extract_relevant_content(field: str, text: str) -> dict:
#     """
#     Extract content relavant to the the specific field.
#     Only the following fields can be used:
#     "requirements", "deadlines", "fees", "scholarships", "university ranking", "subject ranking".

#     IMPORTANT: DO NOT USE THIS FUNCTION for field: {subject} course structure/curiculum
#     Args:
#         field (str): The keyword to look for (must be one of the allowed fields).
#         text (str): The text to search through.

#     Returns:
#         str: Combined snippets of matched sentences with context.

#     """

#     window_size = 4

#     sentences = re.split(r'(?<=[.!?])\s+', text)
#     field_lower = field.lower()
#     indexes = [i for i, sentence in enumerate(sentences) if field_lower in sentence.lower()]
#     if not indexes:
#         return ""
#     snippets = []
#     for idx in indexes:
#         start = max(0, idx - window_size)
#         end = min(len(sentences), idx + window_size + 1)
#         snippet = ' '.join(sentences[start:end]).strip()
#         snippets.append(snippet)

#     return {field: '\n\n'.join(snippets)}
