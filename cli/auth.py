import typer

auth_app = typer.Typer()

@auth_app.command
def register():
    pass

@auth_app.command
def login():
    pass

@auth_app.command
def logout():
    pass
    
if __name__ == '__main__':
    auth_app()