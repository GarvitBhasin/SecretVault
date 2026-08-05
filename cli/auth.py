import typer
import requests

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

    response = requests.post("/register", json=payload)

    if response.ok:
        print("Account successfully created.")
    else:
        print(response.json())

@auth_app.command
def login(username: str, password: str):
    pass

@auth_app.command
def logout():
    pass
    
if __name__ == '__main__':
    auth_app()