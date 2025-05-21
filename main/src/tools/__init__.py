import os

from crewai.tools import BaseTool
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import AzureChatOpenAI
from pydantic import Field

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
