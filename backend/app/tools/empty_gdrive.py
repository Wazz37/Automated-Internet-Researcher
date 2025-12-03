from google.oauth2 import service_account
from googleapiclient.discovery import build

# Your path from the error log
SERVICE_ACCOUNT_FILE = '/docker_shared/LNM/Tool/backend/app/service_account.json'

def empty_trash():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    try:
        # Empty the trash
        service.files().emptyTrash().execute()
        print("Success: Service Account trash emptied.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    empty_trash()