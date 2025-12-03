from app.tools.gdrive_tool import create_gdoc, get_credentials
from app.config import GDRIVE_FOLDER_ID
import json

def test_gdrive():
    print("--- Google Drive Permission Debugger ---")
    
    # 1. Get Credentials and Print Email
    creds = get_credentials()
    if not creds:
        print("ERROR: Could not load credentials.")
        return

    # Extract service account email from the creds object (if possible) or the json file
    try:
        service_account_email = creds.service_account_email
        print(f"\n[IMPORTANT] Service Account Email: {service_account_email}")
        print(f"Please ensure you have SHARED your Google Drive folder with this email address.\n")
    except:
        print("Could not retrieve email from credentials object.")

    print(f"Target Folder ID: {GDRIVE_FOLDER_ID}")

    # 2. Try to create a dummy doc
    print("\nAttempting to create a test document...")
    
    try:
        result = create_gdoc.invoke({
            "topic": "Test Topic",
            "summary": "This is a test summary.",
            "link": "http://example.com",
            "github_results": [],
            "linkedin_post": "Test post content."
        })
        print(f"\nRESULT: {result}")
        
        if "Error" in result:
            print("\n[DIAGNOSIS]")
            if "File not found" in result:
                print("The Folder ID was not found. This usually means:")
                print("1. The Folder ID in .env is incorrect.")
                print("2. OR The folder has NOT been shared with the Service Account email above.")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_gdrive()
