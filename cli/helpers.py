import os, requests
from rich.console import Console 
from dotenv import load_dotenv
load_dotenv()
console = Console()

backend_url = os.getenv("APP_URL")

def get_session():
    if not os.path.exists(".session"):
        console.print("[red]Error:[/red] No user is logged in.")
        return None

    with open(".session", "r") as file:
        token = file.read().strip()

    return token

def remove_session():
    if os.path.exists(".session"):
        os.remove(".session")
        console.print("[green]Success:[/green] Logged out successfully.")
    else:
        console.print("[red]Error:[/red] No user is logged in.")

def add_session(response):
    with open(".session", "w") as file:
        file.write(response.json()["token"])

def send_request(endpoint, payload):
    response = requests.post(f"{backend_url}{endpoint}", json=payload)

    return response

def display_message(response):
    if response.ok:
        console.print(f"[green]Success: [/green]{response.json()["message"]}")
    else:
        console.print(f"[red]Error: [/red]{response.json()["detail"]}")