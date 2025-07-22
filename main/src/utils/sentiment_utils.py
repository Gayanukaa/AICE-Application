import ast
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


def sentiment_reddit_summary(reviews: list[str]) -> dict:
    """
    Given a list of student reviews, fetch 5 related Reddit posts,
    then summarize overall sentiment in 3–4 sentences via an LLM.
    """
    if not reviews:
        raise HTTPException(status_code=400, detail="Must supply at least one review")

    user_review = reviews[0]
    llm = get_llm_instance()

    # Step 1: Generate a better search query using the review
    query_prompt = f"""
    Extract the key topic from the student review below and convert it into a short, focused Reddit search query that would return relevant posts or discussions.

    Review:
    \"\"\"{user_review}\"\"\"

    Return only the search query. Do not include any extra text or punctuation.
    """
    refined_query = llm.invoke([HumanMessage(content=query_prompt)]).content.strip()

    # Step 2: Fetch top 5 Reddit posts with the LLM-generated query
    headers = {"User-Agent": "AICE-App/1.0"}
    try:
        resp = httpx.get(
            "https://www.reddit.com/search.json",
            params={"q": refined_query, "limit": 25},
            headers=headers,
            timeout=10.0,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Reddit search error: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Reddit search failed")

    children = resp.json().get("data", {}).get("children", [])
    raw_posts = [
        {
            "title": item.get("data", {}).get("title", "")[:200],
            "url": f"https://reddit.com{item.get('data', {}).get('permalink', '')}",
        }
        for item in children
    ]

    # Ask LLM to pick top 5 most relevant posts
    ranking_prompt = f"""
    You are an AI assistant. A student wrote this review:
    \"\"\"{user_review}\"\"\"

    Below are 20 Reddit post titles. Select the 5 that are most relevant to the student's review.

    ### Instructions:
    - Return only a Python-style list of exactly 5 post titles (as strings).
    - Titles must be returned **exactly as written below**, preserving spacing, punctuation, and casing.
    - Do not number or alter the titles. Do not add any explanation.

    ### Format:
    ["Exact Title 1","Exact Title 2"]

    Reddit posts:
    {chr(10).join(f"- {p['title']}" for p in raw_posts)}
    """
    top_titles_response = llm.invoke(
        [HumanMessage(content=ranking_prompt)]
    ).content.strip()
    try:
        top_titles = ast.literal_eval(top_titles_response)

        if not isinstance(top_titles, list) or not all(
            isinstance(t, str) for t in top_titles
        ):
            raise ValueError("Invalid format")
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to parse LLM response for selected titles"
        )

    # Match titles to original posts (exact match required)
    posts = [p for p in raw_posts if p["title"] in top_titles][:5]

    # Format list for sentiment analysis
    reddit_list = "\n".join(f"- {p['title']} ({p['url']})" for p in posts)

    sentiment_prompt = f"""
    You are an AI assistant. A student wrote this review:
    \"\"\"{user_review}\"\"\"

    Here are 5 related Reddit posts:
    {reddit_list}

    Please write a 3–4 sentence summary of the overall sentiment across the student review
    and these Reddit discussions, touching on academic quality, campus life,
    student support, career opportunities, and overall satisfaction.
    """
    summary = llm.invoke([HumanMessage(content=sentiment_prompt)]).content.strip()

    return {"reddit_posts": posts, "summary": summary}
