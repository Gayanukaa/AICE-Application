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
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            # azure_api_version=os.getenv("OPENAI_API_VERSION"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
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

    query = reviews[0]

    # 1) Fetch top 5 Reddit posts
    headers = {"User-Agent": "AICE-App/1.0"}
    try:
        resp = httpx.get(
            "https://www.reddit.com/search.json",
            params={"q": query, "limit": 5},
            headers=headers,
            timeout=10.0,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Reddit search error: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Reddit search failed")

    children = resp.json().get("data", {}).get("children", [])
    posts = []
    for item in children:
        d = item.get("data", {})
        title = d.get("title", "")[:200]
        permalink = d.get("permalink", "")
        url = f"https://reddit.com{permalink}"
        posts.append({"title": title, "url": url})

    # 2) Build LLM prompt
    reddit_list = "\n".join(f"- {p['title']} ({p['url']})" for p in posts)
    prompt = f"""
    You are an AI assistant. A student wrote this review:
    \"\"\"{query}\"\"\"

    Here are 5 related Reddit posts:
    {reddit_list}

    Please write a 3–4 sentence summary of the overall sentiment across the student review
    and these Reddit discussions, touching on academic quality, campus life,
    student support, career opportunities, and overall satisfaction.
    """

    # 3) Call the correct LLM client
    llm = get_llm_instance()
    response = llm([HumanMessage(content=prompt)])
    summary = response.content.strip()

    return {"reddit_posts": posts, "summary": summary}
