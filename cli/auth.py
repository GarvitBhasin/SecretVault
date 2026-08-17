import typer
from helpers import *

auth_app = typer.Typer()

@auth_app.command()
def add(
    username: str = typer.Option(..., prompt="Enter a username"),
    email: str = typer.Option(..., prompt="Enter an email"),
    password: str = typer.Option(..., prompt="Enter a password", hide_input=True),
    confirm: str = typer.Option(..., prompt="Confirm password", hide_input=True),
    role: int = typer.Option(..., prompt="Enter user's role (viewer = 1, admin = 2, owner = 3)", )
):

    confirm = confirm_action()

    if confirm:
    
        token = get_session()

        if token is not None:
            response = send_request("post", "/register", {
                "username": username,
                "email": email,
                "password": password,
                "confirm": confirm,
                "role": role
            })

            if response.ok:
                add_session(response)

            display_message(response)

@auth_app.command()
def remove(
    id: int = typer.Option(..., prompt="Enter ID of account to be deleted")
):
    confirm = confirm_action()

    if confirm:
    
        token = get_session()

        if token is not None:
            response = send_request("delete", "/remove", {
                "id": id,
                "token": token
            })

@auth_app.command()
def login(
    email: str = typer.Option(..., prompt="Enter email"),
    password: str = typer.Option(..., prompt="Enter password", hide_input=True)
):
    response = send_request("post", "/login", {
        "email": email,
        "password": password,
    })

    if response.ok:
        add_session(response)

    display_message(response)

@auth_app.command()
def logout():
    remove_session()

@auth_app.command()
def me():

    token = get_session()

    if token is not None:
        response = send_request("get", "/me", {
            "token": token
        })

        display_message(response)

@auth_app.command()
def delete():

    confirm = confirm_action()

    if confirm:

        token = get_session()

        if token is not None:
            response = send_request("delete", "/delete-user", {
                "token": token
            })
             
            if response.ok:
                os.remove(".session")

            display_message(response)

@auth_app.command()
def list():

    token = get_session()
    
    if token is not None:
        response = send_request("get", "/list-user", {
            "token": token
        })

        display_users_table(response.json()["users"])
        display_message(response)