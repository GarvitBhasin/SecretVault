import typer
from helpers import *

projects_app = typer.Typer()

@projects_app.command()
def create(
    name: str = typer.Argument(None)
):
    name = redisplay_prompt(name, "Enter project name")

    token = get_session()

    if token is not None:
        response = send_request("post", "/create-project", {
            "name": name,
            "token": token
        })
        display_message(response)

@projects_app.command()
def delete(
    project_id: str = typer.Argument(None)
):
    project_id = redisplay_prompt(project_id, "Enter project ID")

    token = get_session()

    if token is not None:
        response = send_request("delete", "/delete-project", {
            "id": project_id,
            "token": token
        })

        display_message(response)

@projects_app.command()
def edit():
    pass

@projects_app.command()
def list():
    token = get_session()
    
    if token is not None:
        response = send_request("get", "/list-projects", {
            "token": token
        })

        display_table(response.json()["list"])
        display_message(response)