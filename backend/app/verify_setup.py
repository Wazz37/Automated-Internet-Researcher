import os
from dotenv import load_dotenv, find_dotenv

# Try to find .env file
dotenv_path = find_dotenv()
print(f"Found .env at: {dotenv_path}")
load_dotenv(dotenv_path)

# Check Env Vars
print(f"GDRIVE_FOLDER_ID: {os.getenv('GDRIVE_FOLDER_ID')}")
print(f"GITHUB_ACCESS_TOKEN: {os.getenv('GITHUB_ACCESS_TOKEN')}")

# Check Service Account File
current_dir = os.path.dirname(os.path.abspath(__file__))
service_account_path = os.path.join(current_dir, 'service_account.json')
print(f"Checking for service_account.json at: {service_account_path}")
if os.path.exists(service_account_path):
    print("SUCCESS: service_account.json found.")
else:
    print("FAILURE: service_account.json NOT found.")
