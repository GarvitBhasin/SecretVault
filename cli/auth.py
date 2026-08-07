import typer, os
from helpers import *

auth_app = typer.Typer()

@auth_app.command()
def register(
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    confirm: str = typer.Option(..., prompt=True, hide_input=True),
):
    response = send_request("post", "/register", {
        "username": username,
        "email": email,
        "password": password,
        "confirm": confirm,
    })

    if response.ok:
        add_session(response)

    display_message(response)

@auth_app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
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
        response = send_request("get", "/me", {"token": token})

        display_message(response)

@auth_app.command()
def delete():

    token = get_session()

    if token is not None:
        response = send_request("delete", "/delete", {"token": token}) 
        if response.ok:
            os.remove(".session")

        display_message(response)