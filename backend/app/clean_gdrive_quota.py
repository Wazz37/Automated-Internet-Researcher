from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# Path to your key
SERVICE_ACCOUNT_FILE = '/docker_shared/LNM/Tool/backend/app/service_account.json'

def clean_drive_quota():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"File not found: {SERVICE_ACCOUNT_FILE}")
        return

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    print("Checking storage usage...")
    about = service.about().get(fields="storageQuota").execute()
    quota = about.get('storageQuota', {})
    usage = int(quota.get('usage', 0)) / (1024 * 1024)
    limit = int(quota.get('limit', 0)) / (1024 * 1024)
    print(f"Current Usage: {usage:.2f} MB / {limit:.2f} MB")

    # List files owned by 'me' (the service account) that are NOT in trash
    print("\nListing files owned by Service Account...")
    results = service.files().list(
        q="'me' in owners and trashed=false",
        pageSize=100,
        fields="nextPageToken, files(id, name, size)"
    ).execute()
    
    items = results.get('files', [])

    if not items:
        print('No active files found. Usage might be ghost data or very small files.')
    else:
        print(f"Found {len(items)} files. Deleting now...")
        for item in items:
            try:
                # We interpret 'size' as integer, though sometimes it's string or missing (folders)
                size_str = item.get('size', '0')
                print(f"Deleting: {item['name']} (ID: {item['id']}, Size: {size_str} bytes)")
                service.files().delete(fileId=item['id']).execute()
            except Exception as e:
                print(f"Error deleting {item['name']}: {e}")
        
        print("\nBatch deletion complete. Run again if more files exist (pagination).")

if __name__ == '__main__':
    clean_drive_quota()