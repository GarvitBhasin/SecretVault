import typer
from cli.helpers import *

project_app = typer.Typer()

@project_app.command()
def create(
    name: str = typer.Option(..., prompt="Enter project name")
):
    token = get_session()

    if token is not None:
        response = send_request("post", "/create-project", {
            "name": name,
            "token": token
        })

        display_message(response)

@project_app.command()
def delete(
    id: int = typer.Option(..., prompt="Enter project ID")
):
    confirm = confirm_action()

    if confirm:
    
        token = get_session()

        if token is not None:
            response = send_request("delete", "/delete-project", {
                "id": id,
                "token": token
            })

            display_message(response)

@project_app.command()
def edit(
    id: int = typer.Option(..., prompt="Enter project ID"),
    name: str = typer.Option(..., prompt="Enter new project name")
):
    confirm = confirm_action()

    if confirm:
    
        token = get_session()

        if token is not None:
            response = send_request("patch", "/edit-project", {
                "id": id,
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