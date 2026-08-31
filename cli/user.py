import typer

from cli.helpers.api import create_header, send_request
from cli.helpers.output import confirm_action, display_message, display_users_table
from cli.helpers.session import get_session

user_app = typer.Typer()


@user_app.command()
def create(
    username: str = typer.Option(..., prompt="Enter a username"),
    email: str = typer.Option(..., prompt="Enter an email"),
    password: str = typer.Option(..., prompt="Enter a password", hide_input=True),
    confirm_pass: str = typer.Option(..., prompt="Confirm password", hide_input=True),
    role: int = typer.Option(
        ..., prompt="Enter user's role (viewer = 1, admin = 2, owner = 3)"
    ),
):

    confirm = confirm_action()

    if confirm:
        token = get_session()

        if token is not None:
            response = send_request(
                "post",
                "/user",
                create_header(token),
                {
                    "username": username,
                    "email": email,
                    "password": password,
                    "confirm": confirm_pass,
                    "role": role,
                },
            )

            display_message(response)


@user_app.command()
def delete(id: int = typer.Option(..., prompt="Enter ID of account to be deleted")):
    confirm = confirm_action()

    if confirm:
        token = get_session()

        if token is not None:
            response = send_request("delete", "/user", create_header(token), {"id": id})

        display_message(response)


@user_app.command()
def edit(
    id: int = typer.Option(..., prompt="Enter ID of account to be edited"),
    role: int = typer.Option(
        ..., prompt="Enter user's role (viewer = 1, admin = 2, owner = 3)"
    ),
):
    confirm = confirm_action()

    if confirm:
        token = get_session()

        if token is not None:
            response = send_request(
                "patch", "/user", create_header(token), {"id": id, "role": role}
            )

        display_message(response)


@user_app.command()
def list():

    token = get_session()

    if token is not None:
        response = send_request("get", "/users", {"token": token})

        if response.ok:
            display_users_table(response.json()["users"])

        display_message(response)
