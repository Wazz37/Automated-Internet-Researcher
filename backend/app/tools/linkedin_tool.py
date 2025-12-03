import urllib.parse
import requests
from langchain_core.tools import tool

def shorten_url(long_url: str) -> str:
    """Shortens a URL using TinyURL or is.gd API."""
    # Attempt 1: TinyURL
    try:
        api_url = f"https://tinyurl.com/api-create.php?url={long_url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
        
    # Attempt 2: is.gd (often handles longer URLs better)
    try:
        api_url = f"https://is.gd/create.php?format=simple&url={long_url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass

    return long_url # Fallback to long URL if shortening fails

@tool
def post_to_linkedin(text: str):
    """
    Generates a LinkedIn share URL for the given text.
    
    Args:
        text (str): The content of the post.
        
    Returns:
        str: A message containing the 'Click to Post' URL.
    """
    base_url = "https://www.linkedin.com/feed/"
    params = {
        "shareActive": "true",
        "text": text
    }
    query_string = urllib.parse.urlencode(params)
    share_url = f"{base_url}?{query_string}"
    
    short_url = shorten_url(share_url)
    
    return (
        f"Ready to post! Click the link below to publish to LinkedIn:\n"
        f"{short_url}\n\n"
        f"(If the link doesn't work, copy the text below and paste it manually):\n"
        f"{'-'*20}\n{text}\n{'-'*20}"
    )
