import typer

from cli.helpers.api import create_header, send_request
from cli.helpers.output import display_logs_table, display_message
from cli.helpers.session import get_session

logs_app = typer.Typer()


@logs_app.command()
def list():
    token = get_session()

    if token is not None:
        response = send_request("get", "/logs", create_header(token))

        display_logs_table(response.json()["logs"])
        display_message(response)
