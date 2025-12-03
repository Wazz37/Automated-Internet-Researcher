from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from langgraph.graph import StateGraph, START, END
from app.tools.search_tool import google_search
from app.tools.github_tool import github_search
from app.tools.gdrive_tool import create_gdoc
from app.tools.linkedin_tool import post_to_linkedin
from typing_extensions import TypedDict
from langgraph.prebuilt import ToolNode, tools_condition
from rich import print
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.tools.prioritize_tool import prioritize_tool
from langchain_core.messages import HumanMessage

class AgentState(TypedDict):
    query: str
    search_results: list
    prioritized_results: list
    github_results: list
    summary: str
    content: str
    gdrive_link: str
    linkedin_result: str
    promo_result: str


def search_node(state: AgentState) -> AgentState:
    query = state['query']
    
    # Optimize the query for Google Search using LLM
    import datetime
    current_date = datetime.date.today()
    
    prompt = f"""
    You are an expert at finding the best news on Google. 
    The current date is {current_date}.
    Convert the following user query into a precise and effective Google Search query to find the top, most relevant, and latest news stories from the last week.
    
    User Query: {query}
    
    Return ONLY the optimized search query string, nothing else. Do NOT include the year unless specifically asked, but focus on "latest" or "new".
    """
    optimized_query = ChatOpenAI(model="gpt-4o-mini").invoke(prompt).content.strip()
    
    print(f"Optimized Query: {optimized_query}")
    
    tool_message = google_search.invoke(optimized_query)
    return {'search_results': tool_message} 


def priority_node(state: AgentState) -> AgentState:
    tool_message = prioritize_tool.invoke(
        {'topics': state['search_results']})

    return {'prioritized_results': tool_message}

def github_node(state: AgentState) -> AgentState:
    if not state.get('prioritized_results'):
        print("No prioritized results found. Skipping GitHub search.")
        return {'github_results': []}
        
    top_news = state['prioritized_results'][0]
    query = f"{top_news.title} {top_news.snippet}"
    
    # Use LLM to extract key technical terms for better GitHub search
    prompt = f"""
    Extract 2-3 key technical terms from this news topic to search for related code repositories on GitHub.
    Topic: {top_news.title}
    Snippet: {top_news.snippet}
    
    Return ONLY the search terms separated by space.
    """
    search_terms = ChatOpenAI(model="gpt-4o-mini").invoke(prompt).content.strip()
    print(f"GitHub Search Terms: {search_terms}")
    
    tool_message = github_search.invoke(search_terms)
    return {'github_results': tool_message}

def summary_node(state: AgentState) -> AgentState:
    # Get the top-scored news item (already sorted in priority_node)
    if not state.get('prioritized_results'):
        return {'summary': "No news found to summarize."}
        
    top_news = state['prioritized_results'][0]
    
    prompt = PromptTemplate(template = """
        You are a professional news summarizer. Create a concise but comprehensive summary (4-5 lines) of the following news story.
        Focus on the key facts, impact, and why it matters.
        
        Topic: {title}
        Snippet: {snippet}
        Link: {link}
        
        Also, here are some related GitHub repositories found:
        {github_results}
        
        If the repositories are relevant, mention them briefly in the summary as "Related technical resources".
        """,
        input_variables = ['title', 'snippet', 'link', 'github_results'])

    model = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | model
    res = chain.invoke({
        'title': top_news.title,
        'snippet': top_news.snippet,
        'link': top_news.link,
        'github_results': state.get('github_results', [])
        })

    return {'summary': res.content}

def node_generate_content(state: AgentState):
    if not state.get('prioritized_results'):
        return {"content": {"linkedin_post": "No news found."}}
        
    top_news = state['prioritized_results'][0]
    github_results = state.get('github_results', [])
    topic = top_news.title
    link = top_news.link
    summary = state['summary']

    prompt = f"""
    You are a relatable tech enthusiast chatting with friends. 
    Your goal is to write a LinkedIn post that feels 100% human and 0% corporate/bot.
    
    Topic: {topic}
    Summary: {summary}
    Link: {link}
    
    Related GitHub Repos: {github_results}
    
    Guidelines:
    1. **Voice**: Use simple, everyday words. Write like you're texting a smart friend. If a 5th grader wouldn't understand a word, DON'T use it.
    2. **STRICT PROHIBITIONS**:
       - **NO FANCY WORDS**: Banned words include "delve", "unleash", "game-changer", "revolutionary", "landscape", "tapestry", "fostering", "paramount", "leverage", "synergy", "pivotal", "transformative".
       - **NO EM-DASHES (—)**: Do not use the long dash. Use a simple hyphen (-) or just a comma.
       - **NO FLUFF**: Don't say "In today's fast-paced world". Just get to the point.
    3. **Structure**:
       - **Hook**: Start with a short, punchy sentence or question.
       - **Body**: Explain the news simply. Use a concrete, real-world example. Add a touch of humor or wit if it fits.
       - **Formatting**: Short lines. Easy to read on a phone.
    4. **Call to Action (CTA)**: Ask a simple question.
    5. **Hashtags**: 3-5 relevant tags.
    6. **Length**: STRICTLY keep the total post under 800 characters.
    
    Output JSON with:
    - linkedin_post: The full post content (including the link at the end or in the body naturally).
    - twitter_thread: A list of 3-5 tweets for a thread on the same topic.
    - hooks: 3 alternative hooks for the LinkedIn post.
    - hashtags: A list of 10 relevant hashtags.
    
    Ensure the output is valid JSON.
    """

    result = ChatOpenAI(model="gpt-4o-mini").invoke([HumanMessage(content=prompt)]).content

    import json
    # Clean up potential markdown formatting in response (e.g. ```json ... ```)
    cleaned_result = result.replace("```json", "").replace("```", "").strip()
    
    return {"content": json.loads(cleaned_result)}

def gdrive_node(state: AgentState) -> AgentState:
    content = state['content']
    if not state.get('prioritized_results'):
        return {'gdrive_link': "No content to save."}
        
    top_news = state['prioritized_results'][0]
    
    data = {
        'topic': top_news.title,
        'link': top_news.link,
        'summary': state['summary'],
        'github_results': state.get('github_results', []),
        'linkedin_post': content.get('linkedin_post', '')
    }
    
    # Pass the dictionary directly, LangChain will map keys to function arguments
    tool_message = create_gdoc.invoke(data)
    print(f"GDrive Result: {tool_message}")
    
    return {'gdrive_link': tool_message}

def linkedin_node(state: AgentState) -> AgentState:
    content = state['content']
    if not content or 'linkedin_post' not in content:
        return {'linkedin_result': "No content to post."}
        
    post_text = content['linkedin_post']
    
    # Add hashtags if available
    if 'hashtags' in content and isinstance(content['hashtags'], list):
        tags = " ".join(content['hashtags'])
        post_text += f"\n\n{tags}"
        
    print(f"\n{'='*40}\nDRAFT LINKEDIN POST:\n{post_text}\n{'='*40}\n")
    
    # Generate Smart Link
    tool_message = post_to_linkedin.invoke(post_text)
    print(f"\n{tool_message}\n")
    
    return {'linkedin_result': tool_message}

def project_promo_node(state: AgentState) -> AgentState:
    """
    Generates a LinkedIn post about THIS project (the News Content Generator).
    """
    prompt = """
    Write a short, funny, and engaging LinkedIn post announcing a new Python project I built, targeted to developers, AI engineers, and tech leaders.

    Project Name: “Automated News Content Generator & LinkedIn Auto-Poster”

    Project capabilities:
    - Uses Google Search API to fetch the latest trending tech news.
    Write a short, funny LinkedIn post about a Python project I just built.
    
    Project Name: “Automated Internet Researcher & LinkedIn Auto-Poster”

    Project capabilities:
    - Searches the internet (Google Search API) for the latest and most relevant content on ANY topic I provide — not just tech news.
    - Finds related GitHub repositories, research papers, blog articles, or resources to support the topic.
    - Uses an AI Agent (LangChain / LangGraph) to analyze the collected information and automatically generate a high-quality LinkedIn post based on the insights.
    - Creates a one-click “Post to LinkedIn” publishing link that automatically uploads the generated post — no manual typing or copy-paste needed.
    - After posting, automatically saves the content in Markdown (.md) format to my Google Drive for versioning, documentation, and future automation workflows.

    
    The Twist: Mention that THIS post itself was written by the tool.
    
    Guidelines:
    1. **Voice**: Reddit style. Super casual. Lowercase is fine. "i built a thing".
    2. **NO FANCY WORDS**: If it sounds like a marketing team wrote it, delete it. No "leverage", "synergy", "revolutionary", "excited to announce".
    3. **NO EM-DASHES**.
    4. **Length**: Under 800 characters.
    5. **Hashtags**: #Python #Automation #LazyDev
    
    Return ONLY the post text. No JSON.
    """
    
    post_text = ChatOpenAI(model="gpt-4o-mini").invoke([HumanMessage(content=prompt)]).content.strip()
    
    print(f"\n{'='*40}\nDRAFT PROMO POST:\n{post_text}\n{'='*40}\n")
    
    # Generate Smart Link
    tool_message = post_to_linkedin.invoke(post_text)
    print(f"\n[PROJECT PROMO LINK]\n{tool_message}\n")
    
    return {'promo_result': tool_message}

graph = StateGraph(AgentState)

graph.add_node('search', search_node)
graph.add_node('summary', summary_node)
graph.add_node('priority_node', priority_node)
graph.add_node('github_node', github_node)
graph.add_node("content", node_generate_content)
graph.add_node("gdrive", gdrive_node)
graph.add_node("linkedin", linkedin_node)
graph.add_node("project_promo", project_promo_node)

graph.add_edge(START, 'search')
graph.add_edge('search', 'priority_node')
graph.add_edge('priority_node', 'github_node')
graph.add_edge('github_node', 'summary')
graph.add_edge('summary', 'content')
graph.add_edge('content', 'gdrive')
graph.add_edge('gdrive', 'linkedin')
graph.add_edge('linkedin', 'project_promo')
graph.add_edge('project_promo', END)

workflow = graph.compile()

if __name__ == "__main__":
    user_query = input("Enter your search query (e.g., 'latest AI news'): ").strip()
    if not user_query:
        user_query = "Latest news about technology"
        
    print(f"\nRunning search for: {user_query}...\n")
    res = workflow.invoke({'query': user_query})
    print("\nWorkflow Completed.")