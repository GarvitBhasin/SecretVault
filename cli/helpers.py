import os, requests, typer
from rich.console import Console 
from rich.table import Table, box
from dotenv import load_dotenv
load_dotenv()

console = Console()
table = Table(title="Projects", header_style="bold", expand=True, show_lines=True, box=box.ROUNDED)
backend_url = os.getenv("APP_URL")

def get_session():
    if not os.path.exists(".session"):
        console.print("[red]Error[/red]: No user is logged in.")
        return None

    with open(".session", "r") as file:
        token = file.read().strip()

    return token

def remove_session():
    if os.path.exists(".session"):
        os.remove(".session")
        console.print("[green]Success[/green]: Logged out .")
    else:
        console.print("[red]Error[/red]: No user is logged in.")

def add_session(response):
    with open(".session", "w") as file:
        file.write(response.json()["token"])

def send_request(method, endpoint, payload):
    return requests.request(
        method, 
        f"{backend_url}{endpoint}",
        json=payload
    )

def display_message(response):
    if response.ok:
        console.print(f"[green]Success[/green]: {response.json()["message"]}")
    else:
        console.print(f"[red]Error[/red]: {response.json()["detail"]}")

def display_table(projects):
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Creator")
    table.add_column("Secrets")

    for project in projects:
        table.add_row(
            project["id"],
            project["name"],
            project["creator"],
            project["secrets"]
        )

    console.print(table)

def redisplay_prompt(variable, prompt):
    if variable is None:
        variable = typer.prompt(prompt)
    return variable