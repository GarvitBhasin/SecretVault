import typer

from cli.helpers.api import create_header, send_request
from cli.helpers.output import confirm_action, display_message, display_projects_table
from cli.helpers.session import get_session

project_app = typer.Typer()


@project_app.command()
def create(name: str = typer.Option(..., prompt="Enter project name")):
    token = get_session()

    if token is not None:
        response = send_request(
            "post", "/project", create_header(token), {"name": name}
        )

        display_message(response)


@project_app.command()
def delete(id: int = typer.Option(..., prompt="Enter project ID")):
    confirm = confirm_action()

    if confirm:
        token = get_session()

        if token is not None:
            response = send_request(
                "delete",
                f"/projects/{id}",
                create_header(token),
            )

            display_message(response)


@project_app.command()
def edit(
    id: int = typer.Option(..., prompt="Enter project ID"),
    name: str = typer.Option(..., prompt="Enter new project name"),
):
    confirm = confirm_action()

    if confirm:
        token = get_session()

        if token is not None:
            response = send_request(
                "patch", f"/projects/{id}", create_header(token), {"name": name}
            )

            display_message(response)


@project_app.command()
def list():
    token = get_session()

    if token is not None:
        response = send_request("get", "/projects", create_header(token))

        if response.ok:
            display_projects_table(response.json()["projects"])

        display_message(response)
