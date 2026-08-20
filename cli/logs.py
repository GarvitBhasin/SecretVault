import typer
from cli.helpers import *

logs_app = typer.Typer()

@logs_app.command()
def list():
    token = get_session()

    if token is not None:
        response = send_request("get", "/logs", {"token": token})

        display_logs_table(response.json()["logs"])
        display_message(response)