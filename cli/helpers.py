import os, requests, typer
from rich.console import Console 
from rich.table import Table, box
from dotenv import load_dotenv
load_dotenv()

console = Console()
projects_table = Table(title="Projects", header_style="bold", expand=True, box=box.ROUNDED)
secrets_table = Table(title="Secrets", header_style="bold", expand=True, box=box.ROUNDED)
backend_url = os.getenv("APP_URL")

# SESSION HELPERS

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
        console.print("[green]Success[/green]: Logged out.")

    else:
        console.print("[red]Error[/red]: No user is logged in.")

def add_session(response):
    with open(".session", "w") as file:
        file.write(response.json()["token"])

# API HELPERS

def send_request(method, endpoint, payload):
    return requests.request(
        method, 
        f"{backend_url}{endpoint}",
        json=payload
    )

# FRONTEND HELPERS

def display_message(response):
    if response.ok:
        console.print(f"[green]Success[/green]: {response.json()["message"]}")
    else:
        console.print(f"[red]Error[/red]: {response.json()["detail"]}")

def display_projects_table(projects):
    projects_table.add_column("ID")
    projects_table.add_column("Name")
    projects_table.add_column("Creator")
    projects_table.add_column("Secrets")
    projects_table.add_column("Created At")
    projects_table.add_column("Last Updated")

    for project in projects:
        projects_table.add_row(
            project["id"],
            project["name"],
            project["creator"],
            project["secrets"],
            project["created_at"],
            project["updated_at"],
        )

    console.print(projects_table)

def display_secrets_table(secrets):
    secrets_table.add_column("ID")
    secrets_table.add_column("Name")
    secrets_table.add_column("Creator")
    secrets_table.add_column("Created Date")
    secrets_table.add_column("Last Updated")

    for secret in secrets: 
        secrets_table.add_row(
            secret["id"],
            secret["name"],
            secret["creator"],
            secret["created_at"],
            secret["updated_at"],
        )

    console.print(secrets_table)

def confirm_action():
    return typer.confirm("Are you sure you want to execute this action?")