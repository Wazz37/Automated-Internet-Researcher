# Automated News Content Generator

This tool automates the process of finding the latest tech news, generating engaging LinkedIn posts, and saving them to Google Drive. It uses AI to ensure the content is high-quality and human-like.

## Features
- **Smart Search**: Finds the most relevant and recent news using Google Search API.
- **GitHub Integration**: Discovers related code repositories to add technical depth.
- **AI Content Generation**: Writes viral-style LinkedIn posts (and a promo post for this tool!).
- **Smart Links**: Generates a one-click "Post to LinkedIn" URL.
- **Google Drive Backup**: Saves your posts and summaries to a Google Doc.

## Setup

1.  **Clone the repository**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure you have `langchain`, `langgraph`, `openai`, `google-api-python-client`, `requests` installed)*

3.  **Configure Environment Variables**:
    Create a file named `.env` in the root directory. Copy the template below and fill in your API keys.

    **`.env` Template:**
    ```env
    # OpenAI API Key for the AI Agent
    OPENAI_API_KEY="sk-..."

    # Google Search API (for finding news)
    GOOGLE_API_KEY="AIza..."
    GOOGLE_CX="0123..."

    # GitHub Access Token (for finding code)
    GITHUB_ACCESS_TOKEN="ghp_..."

    # Google Drive Folder ID (where docs will be saved)
    GDRIVE_FOLDER_ID="1abc..."
    ```

    *Note: You do NOT need LinkedIn API keys. The tool uses a Smart Link strategy.*

## How to Run

Run the main script:
```bash
python3 -m app.graph
```

You will be asked to enter a search query (e.g., "latest AI news"). The tool will handle the rest!
