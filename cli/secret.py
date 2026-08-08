import typer
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
def delete():
    pass

@secrets_app.command()
def edit():
    pass

@secrets_app.command()
def list(
    project_id: str = typer.Argument(None)
):
    token = get_session()
    
    project_id = redisplay_prompt(project_id, "Enter project ID")

    if token is not None:
        response = send_request("get", "/list-secrets", {
            "id": project_id,
            "token": token
        })

        if response.ok:
            display_secrets_table(response.json()["secrets"])
        display_message(response)

@secrets_app.command()
def get():
    pass