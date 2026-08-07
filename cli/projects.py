import typer
from helpers import *

projects_app = typer.Typer()

@projects_app.command()
def create(
    name: str = typer.Option(..., prompt=True)
):
    token = get_session()

    if token is not None:
        response = send_request("post", "/create-project", {
            "name": name,
            "token": token
        })
        display_message(response)

@projects_app.command()
def delete():
    pass

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