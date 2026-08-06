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
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "confirm": confirm,
    }

    response = send_request("/register", payload)

    with open(".session", "w") as file:
        file.write(response.json()["token"])

    if response.ok:
        print(response.json()["message"])
    else:
        print(response.json()["detail"])

@auth_app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    payload = {
        "email": email,
        "password": password
    }

    response = send_request("/login", payload)

    with open(".session", "w") as file:
        file.write(response.json()["token"])

    print(response.json()["message"])

@auth_app.command()
def logout():

    if os.path.exists(".session"):
        os.remove(".session")
        print("Logged out successfully.")
    else:
        print("Please log in first")

@auth_app.command()
def me():

    token = get_session()

    if token is not None:
        response = send_request("/me", {"token": token})

        print(f"Username: {response.json()["username"]}")
        print(f"Email: {response.json()["email"]}")

@auth_app.command()
def delete():

    token = get_session()
    
    response = send_request("/delete", { "token": token })

    if response.ok:
        os.remove(".session")
        print(response.json()["message"])
    else:
        print(response.json()["detail"])