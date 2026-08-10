import typer
from typing import Optional
from helpers import *

secrets_app = typer.Typer()

@secrets_app.command()
def create(
    project_id: str = typer.Option(..., prompt="Enter project ID"),
    name: str = typer.Option(..., prompt="Enter secret name"),
    value: str = typer.Option(..., prompt="Enter secret"),
):
    token = get_session()

    if token is not None:
        response = send_request("post", "/create-secret", {
            "project_id": project_id,
            "name": name,
            "value": value,
            "token": token
        })

        display_message(response)

@secrets_app.command()
def delete(
    secret_id: str = typer.Argument(None)
):
    token = get_session()
    
    secret_id = redisplay_prompt(secret_id, "Enter project ID")

    if token is not None:
        response = send_request("delete", "/delete-secret", {
            "id": secret_id,
            "token": token
        })

        display_message(response)

@secrets_app.command()
def edit(
    secret_id: str = typer.Option(..., prompt="Enter secret ID"),
):
    name = typer.prompt(
        "Enter new secret name",
        default="",
        show_default=False
    )

    value = typer.prompt(
        "Enter new secret value",
        default="",
        show_default=False
    )

    if not (name and value):
        console.print("[red]Error[/red]: Nothing to edit.")
        return
    
    token = get_session()
    
    if token is not None:
        response = send_request("patch", "/edit-secret", {
            "id": secret_id,
            "token": token,
            "name": name if name else None,
            "value": value if value else None
        })

        display_message(response)

@secrets_app.command()
def list(
    project_id: str = typer.Argument(None)
):
    token = get_session()
    
    project_id = redisplay_prompt(project_id, "Enter project ID")

    if token is not None:
        response = send_request("get", "/list-secret", {
            "id": project_id,
            "token": token
        })

        if response.ok:
            display_secrets_table(response.json()["secrets"])
        display_message(response)

@secrets_app.command()
def get():
    pass