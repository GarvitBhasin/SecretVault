import typer
import requests

secrets_app = typer.Typer()

@secrets_app.command
def create():
    pass

@secrets_app.command
def delete():
    pass

@secrets_app.command
def edit():
    pass

@secrets_app.command
def list():
    pass

@secrets_app.command
def get():
    pass