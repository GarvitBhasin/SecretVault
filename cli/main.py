import typer
from auth import auth_app
from secret import secrets_app
from projects import projects_app
from logs import logs_app

app = typer.Typer()

app.add_typer(auth_app, name="auth")
app.add_typer(secrets_app, name="secrets")
app.add_typer(projects_app, name="projects")
app.add_typer(logs_app, name="logs")

if __name__ == '__main__':
    app()