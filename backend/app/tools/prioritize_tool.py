from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List

class TopicScore(BaseModel):
    title: str
    score: float
    reason: str
    snippet: str
    link: str

class TopicScoreList(BaseModel):
    items: List[TopicScore]

llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(TopicScoreList)

@tool
def prioritize_tool(topics: list) -> list:
    """
    Takes list of topics from search tool.
    Returns a list of scored topics sorted by score.
    Uses ChatOpenAI to generate scores.
    """
    prompt = f"""
    You are an expert content strategist. Analyze the following news topics and score them (0–100) based on their potential to go viral on LinkedIn and social media.
    
    Scoring Criteria:
    - **Impact**: How significant is this news?
    - **Novelty**: Is it new and cutting-edge?
    - **Engagement**: Will it spark discussion or debate?
    - **Professional Relevance**: Is it valuable for a professional audience (LinkedIn)?

    Return a JSON object with a list of items, where each item contains:
    - title: The original title
    - score: The calculated score (0-100)
    - reason: A brief explanation of the score
    - snippet: The original snippet (preserve this exactly)
    - link: The original link (preserve this exactly)

    Topics: {topics}
    """

    res = llm.invoke(prompt)
    
    # Sort by score in descending order to ensure the best topics are first
    sorted_items = sorted(res.items, key=lambda x: x.score, reverse=True)
    
    return sorted_items


