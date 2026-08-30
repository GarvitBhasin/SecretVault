import typer
from cli.helpers import *

secrets_app = typer.Typer()

@secrets_app.command()
def create(
    id: int = typer.Option(..., prompt="Enter project ID"),
    name: str = typer.Option(..., prompt="Enter secret name"),
    value: str = typer.Option(..., prompt="Enter secret"),
):
    description: str = typer.prompt("Enter secret description (optional)", default="", show_default=False)
    
    token = get_session()

    if token is not None:
        response = send_request(
            "post", 
            "/create-secret", 
            create_header(token),
            {
                "id": id,
                "name": name,
                "value": value,
                "description": description if description else None
            }
        )

        display_message(response)

@secrets_app.command()
def delete(
    id: int = typer.Option(..., prompt="Enter secret ID")
):
    confirm = confirm_action()

    if confirm:
    
        token = get_session()

        if token is not None:
            response = send_request(
                "delete", 
                "/delete-secret",
                create_header(token), 
                {
                    "id": id,
                }
            )

            display_message(response)

@secrets_app.command()
def edit(
    id: int = typer.Option(..., prompt="Enter secret ID"),
):
    name: str = typer.prompt("Enter new secret name", default="", show_default=False)
    value: str = typer.prompt("Enter new secret value", default="", show_default=False)
    description: str = typer.prompt("Enter new description", default="", show_default=False)

    if name == "" or value == "":
        console.print("[red]Error[/red]: Name/value field(s) cannot be empty.")
        return

    confirm = confirm_action()

    if confirm:
    
        token = get_session()
        
        if token is not None:
            response = send_request(
                "patch", 
                "/edit-secret", 
                create_header(token),
                {
                    "id": id,
                    "description": description,
                    "name": name,
                    "value": value
                }
            )

            display_message(response)

@secrets_app.command()
def list(
    id: int = typer.Option(..., prompt="Enter project ID")
):
    token = get_session()

    if token is not None:
        response = send_request(
            "get", 
            "/list-secret",
            create_header(token), 
            {
                "id": id
            }
        )

        if response.ok:
            display_secrets_table(response.json()["secrets"])

        display_message(response)

@secrets_app.command()
def get(
    id: int = typer.Option(..., prompt="Enter secret ID")
):
    confirm = confirm_action()

    if confirm:

        token = get_session()

        if token is not None:
            response = send_request(
                "get", 
                "/get-secret",
                create_header(token), 
                {
                    "id": id,
                }
            )

        if response.ok:
            print(response.json()["secret"])

        display_message(response)