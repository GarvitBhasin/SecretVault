from fastapi import FastAPI
from models import *
from sqlalchemy.orm import sessionmaker

app = FastAPI()

app.post("/register")
def register():
    user = Users(

    )


if __name__ == '__main__':
    app()