import typer
from helpers import *

project_app = typer.Typer()

@project_app.command()
def create(
    name: str = typer.Argument(None)
):
    token = get_session()

    name = redisplay_prompt(name, "Enter project name")

    if token is not None:
        response = send_request("post", "/create-project", {
            "name": name,
            "token": token
        })

        display_message(response)

@project_app.command()
def delete(
    project_id: str = typer.Argument(None)
):
    token = get_session()

    project_id = redisplay_prompt(project_id, "Enter project ID")


    if token is not None:
        response = send_request("delete", "/delete-project", {
            "id": project_id,
            "token": token
        })

        display_message(response)

@project_app.command()
def edit(
    project_id: str = typer.Option(..., prompt="Enter project ID"),
    name: str = typer.Option(..., prompt="Enter new project name")
):
    token = get_session()

    if token is not None:
        response = send_request("patch", "/edit-project", {
            "id": project_id,
            "token": token,
            "name": name
        })

        display_message(response)

@project_app.command()
def list():
    token = get_session()
    
    if token is not None:
        response = send_request("get", "/list-project", {
            "token": token
        })

        if response.ok:
            display_projects_table(response.json()["projects"])
        display_message(response)