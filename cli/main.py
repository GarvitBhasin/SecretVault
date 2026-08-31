import typer

from cli.auth import auth_app
from cli.helpers.api import send_request
from cli.helpers.output import console, display_message
from cli.logs import logs_app
from cli.project import project_app
from cli.secret import secrets_app
from cli.user import user_app

app = typer.Typer()


@app.command()
def init():
    console.print("[Green]-------------------------[/Green]")
    console.print("SecretVault Initial Setup")
    console.print("[Green]-------------------------[/Green]")

    username = typer.prompt("Enter username")
    email = typer.prompt("Enter email")
    password = typer.prompt("Enter password", hide_input=True)
    confirm = typer.prompt("Confirm password", hide_input=True)

    response = send_request(
        "post",
        "/init",
        {
            "username": username,
            "email": email,
            "password": password,
            "confirm": confirm,
        },
    )

    display_message(response)


app.add_typer(auth_app, name="auth")
app.add_typer(user_app, name="users")
app.add_typer(secrets_app, name="secrets")
app.add_typer(project_app, name="projects")
app.add_typer(logs_app, name="logs")

if __name__ == "__main__":
    app()
