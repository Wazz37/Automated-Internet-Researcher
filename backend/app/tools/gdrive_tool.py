from google.oauth2 import service_account
from googleapiclient.discovery import build
from langchain_core.tools import tool
from ..config import GDRIVE_FOLDER_ID
import datetime

import os

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
# Construct absolute path to service_account.json (assumed to be in app/ directory, one level up from tools/)
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'service_account.json')

def get_credentials():
    print(f"Looking for service account file at: {SERVICE_ACCOUNT_FILE}")
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"File not found at {SERVICE_ACCOUNT_FILE}")
        return None
        
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return creds
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None

@tool
def create_gdoc(topic: str, summary: str, link: str, github_results: list, linkedin_post: str) -> str:
    """
    Creates a Google Doc with the provided content.
    """
    creds = get_credentials()
    if not creds:
        return "Error: Could not load service_account.json"

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        title = f"Research: {topic} - {datetime.date.today()}"
        
        # 1. Create the blank file
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        if GDRIVE_FOLDER_ID:
            file_metadata['parents'] = [GDRIVE_FOLDER_ID]

        doc = drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
        doc_id = doc.get('id')
        web_link = doc.get('webViewLink')

        # 2. Write content to the file
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': f"TOPIC: {topic}\n\n"
                            f"LINK: {link}\n\n"
                            f"SUMMARY:\n{summary}\n\n"
                            f"GITHUB REPOS:\n{github_results}\n\n"
                            f"----------------------------------------\n"
                            f"DRAFT LINKEDIN POST:\n\n"
                            f"{linkedin_post}\n"
                }
            }
        ]

        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        return f"Document created successfully: {web_link}"

    except Exception as e:
        print(f"GDrive Error: {e}")
        # Fallback to local file
        filename = f"research_report_{datetime.date.today()}.md"
        with open(filename, "w") as f:
            f.write(f"# TOPIC: {topic}\n\n")
            f.write(f"**LINK**: {link}\n\n")
            f.write(f"## SUMMARY\n{summary}\n\n")
            f.write(f"## GITHUB REPOS\n{github_results}\n\n")
            f.write(f"---\n")
            f.write(f"## DRAFT LINKEDIN POST\n\n{linkedin_post}\n")
            
        return f"GDrive failed (Quota/Auth). Saved locally to: {os.path.abspath(filename)}"
