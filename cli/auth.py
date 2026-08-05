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

    response = requests.post("http://127.0.0.1:8000/register", json=payload)

    
    print(response.status_code)
    print(response.text)

@auth_app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    payload = {
        "email": email,
        "password": password
    }

    response = requests.post("http://127.0.0.1:8000/login", json=payload)

    print(response.status_code)
    print(response.text)

@auth_app.command()
def logout():
    pass
    
if __name__ == '__main__':
    auth_app()