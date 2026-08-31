import os

from rich.console import Console

console = Console()


def get_session():
    if not os.path.exists(".session"):
        console.print("[red]Error[/red]: No user is logged in.")
        return None

    with open(".session") as file:
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
