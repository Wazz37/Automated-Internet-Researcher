import requests
from langchain_core.tools import tool
from ..config import GITHUB_ACCESS_TOKEN

@tool
def github_search(query: str) -> list:
    """
    Search GitHub for repositories related to the query.
    Returns top 3 repositories with name, description, stars, and link.
    """
    url = "https://api.github.com/search/repositories"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_ACCESS_TOKEN:
        headers["Authorization"] = f"token {GITHUB_ACCESS_TOKEN}"

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 3
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        if "items" in data:
            for item in data["items"]:
                results.append({
                    "name": item.get("full_name"),
                    "description": item.get("description"),
                    "stars": item.get("stargazers_count"),
                    "link": item.get("html_url")
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]
