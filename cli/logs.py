import typer
import requests

logs_app = typer.Typer()

@logs_app.command()
def list():
    pass