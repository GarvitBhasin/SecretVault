import os, requests
from dotenv import load_dotenv
load_dotenv()

backend_url = os.getenv("APP_URL")

def get_session():
    if not os.path.exists(".session"):
        print("Please log in first.")
        return None

    with open(".session", "r") as file:
        token = file.read().strip()

    return token

def send_request(endpoint, payload):
    response = requests.post(f"{backend_url}{endpoint}", json=payload)

    return response