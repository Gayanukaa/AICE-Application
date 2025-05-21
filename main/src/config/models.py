from typing import List

from pydantic import BaseModel


class SentimentRequest(BaseModel):
    reviews: List[str]


class RedditPost(BaseModel):
    title: str
    url: str


class SentimentResponse(BaseModel):
    reddit_posts: List[RedditPost]
    summary: str
