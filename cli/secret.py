import typer
from helpers import *

secrets_app = typer.Typer()

@secrets_app.command
def create(
    id: str = typer.Option(..., prompt="Enter project ID"),
    name: str = typer.Option(..., prompt="Enter secret name"),
    value: str = typer.Option(..., prompt="Enter secret"),
):
    token = get_session()

    if token is not None:
        response = send_request("post", "/create-secret", {
            "id": id,
            "name": name,
            "value": value,
            "token": token
        })

        display_message(response)

@secrets_app.command
def delete():
    pass

@secrets_app.command
def edit():
    pass

@secrets_app.command
def list():
    pass

@secrets_app.command
def get():
    pass