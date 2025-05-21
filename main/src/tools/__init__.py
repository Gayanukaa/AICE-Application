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
def fetch_university_admission_info(university_name: str, field: str, level: str) -> str:
    """
    Retrieves specific admission-related information for a given university and level of study 
    by scraping or querying relevant web sources.

    Args:
        university_name (str): Name of the university to retrieve information from.
        field (str): The specific admission-related detail to retrieve. 
                     Possible values include:
                        - "requirements"
                        - "deadlines"
                        - "fees"
                        - "scholarships"
                        - "university ranking"
                        - "subject ranking"
                        - "{subject} course structure"
        level (str): Level of study (e.g., "undergraduate", "postgraduate").

    Returns:
        str: Extracted information related to the requested field for the given university and level of study.
    """

    def extract_main_links(data):
        links = []
        for item in data.get('organic', []):
            if 'link' in item:
                links.append(item['link'])
        return links
    
    try:
        response = search_uni.run(search_query=f"{university_name} {level} {field} site")
        urls = extract_main_links(response)         #Extract main links from response

        if not urls:
            result = "No relevant URL found."

        url = urls[0]           #Select the first link
        
        result = ScrapeWebsiteTool(website_url=url).run()

    except Exception as e:
            result = f"Error: {str(e)}"

    return result



@tool("extract_relavant_content")
def extract_relevant_content(field: str, text: str) -> str:
    """
    Finds sentences containing a keyword in a text and returns those sentences with some surrounding context.  
    Only the following fields can be used:  
    "requirements", "deadlines", "fees", "scholarships", "university ranking", "subject ranking".

    Args:
        field (str): The keyword to look for (must be one of the allowed fields).
        text (str): The text to search through.
        
    Returns:
        str: Combined snippets of matched sentences with context.

    """

    window_size = 5

    sentences = re.split(r'(?<=[.!?])\s+', text)
    field_lower = field.lower()
    indexes = [i for i, sentence in enumerate(sentences) if field_lower in sentence.lower()]
    if not indexes:
        return ""
    snippets = []
    for idx in indexes:
        start = max(0, idx - window_size)
        end = min(len(sentences), idx + window_size + 1)
        snippet = ' '.join(sentences[start:end]).strip()
        snippets.append(snippet)

    return '\n\n'.join(snippets)
