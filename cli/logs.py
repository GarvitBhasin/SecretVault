import typer

logs_app = typer.Typer()

@logs_app.command
def list():
    pass
    
if __name__ == '__main__':
    logs_app()