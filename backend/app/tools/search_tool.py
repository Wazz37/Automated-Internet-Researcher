import requests
from langchain_core.tools import tool
from ..config import GOOGLE_API_KEY, GOOGLE_CX
from rich import print
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# llm = ChatOpenAI()

@tool
def google_search(query: str) -> list:
    """
    Perform a REAL Google Search using Google Custom Search API.
    Returns top 5 results: title, snippet, and link.
    """

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": 5,
        "dateRestrict": "w1", # Restrict to past week
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    if "items" in data:
        for item in data["items"]:
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link")
            })

    return results

# res = google_search.invoke("News about AI today")
# print(res)


# query = "News about AI today"
# messages = [HumanMessage(content = query)]

# llm_with_tool = llm.bind_tools([google_search])
# ai_response = llm_with_tool.invoke(messages)

# print(ai_response)

# messages.append(ai_response)

# tool_response = google_search.invoke(ai_response.tool_calls[0])

# messages.append(tool_response)
# print(tool_response)

# print(llm_with_tool.invoke(messages).content)