import typer

projects_app = typer.Typer()

@projects_app.command
def create():
    pass

@projects_app.command
def delete():
    pass

@projects_app.command
def edit():
    pass

@projects_app.command
def list():
    pass
    
if __name__ == '__main__':
    projects_app()