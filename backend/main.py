from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from sqlalchemy import String, ForeignKey, create_engine, select, delete, func
from pydantic import BaseModel
from pwdlib import PasswordHash
from backend.token import *
from dotenv import load_dotenv
load_dotenv()
import re, os

database_url = os.getenv("DB_URL")
app = FastAPI()
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)
password_hash = PasswordHash.recommended()

# DB MODELS

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

class Projects(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

class Secrets(Base):
    __tablename__ = "secrets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

Base.metadata.create_all(engine)

# REQUEST TEMPLATES

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenRequest(BaseModel):
    token: str

class CreateRequest(BaseModel):
    token: str
    name: str

# AUTH

@app.post("/register", status_code=201)
def register(data: RegisterRequest):

    # Check email validity
    email_valid = bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", data.email))

    if not email_valid:
        raise HTTPException(
            status_code=422,
            detail="Invalid email."
        )

    # Check password pairs
    if data.confirm != data.password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match."
        )

    # Check password strength
    has_char = any(char.isalpha() for char in data.password)
    has_digit = any(char.isdigit() for char in data.password)
    has_symbol = any(not char.isalnum() for char in data.password)
    is_long = len(data.password) > 8

    if not (has_char and has_digit and has_symbol and is_long):
        raise HTTPException(
            status_code=422,
            detail="Password must have at least one character, digit, symbol and be more than 8 characters long."
        )

    try:
        session = SessionLocal()

        # Check for duplicate email or username
        existing_email = session.execute(
            select(Users).where(Users.email == data.email)
        ).scalar_one_or_none()

        existing_username = session.execute(
            select(Users).where(Users.username == data.username)
        ).scalar_one_or_none()

        if existing_email:
            raise HTTPException(
                status_code=409,
                detail="Email is already registered."
            ) 
        if existing_username:
            raise HTTPException(
                status_code=409,
                detail="Username taken."
            ) 

        # Hash password
        hashed_pass = password_hash.hash(data.password)

        # Create user
        user = Users(
            username = data.username,
            email = data.email,
            password_hash = hashed_pass,
        )
    
        session.add(user)
        session.commit()

        # Return token and message
        id = session.execute(select(Users.id).where(Users.email == data.email)).scalar_one()
        print(id)
        token = encode_token({ "sub": str(id) })
                
        return {
            "token": token,
            "token_type": "bearer",
            "message": "Account created."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.post("/login")
def login(data: LoginRequest):

    try:
        session = SessionLocal()

        # find user in db with corelating hash and id
        result = session.execute(select(Users.password_hash, Users.id).where(Users.email == data.email)).first()

        if result is None:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password."
            )

        stored_hash, id = result

        # Check if password is correct
        is_valid = password_hash.verify(data.password, stored_hash)

        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password."
            )

        # Return token and message
        token = encode_token({"sub": str(id)})
        
        return {
            "token": token,
            "token_type": "bearer",
            "message": "Logged in."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/me")
def me(data: TokenRequest):
    payload = decode_token(data.token)
    id = int(payload["sub"])

    try:
        session = SessionLocal()

        result = session.execute(select(Users.username, Users.email).where(Users.id == id)).first()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        username, email = result

        return {
            "username": username,
            "email": email,
        }

    finally:
        session.close()

@app.post("/delete")
def delete_user(data: TokenRequest):
    payload = decode_token(data.token)
    id = int(payload["sub"])

    try:
        session = SessionLocal()

        result = session.execute(delete(Users).where(Users.id == id))
        session.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        return {
            "message": "Account deleted."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# PROJECTS

@app.post("/create-project", status_code=201)
def create_project(data: CreateRequest):

    payload = decode_token(data.token)
    id = int(payload["sub"])

    try:
        session = SessionLocal()

        project = Projects(
            name = data.name,
            creator_id = id
        )

        session.add(project)
        session.commit()

        return {
            "message": "Project created."
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@app.get("/list-projects")
def list_projects(data: TokenRequest):

    payload = decode_token(data.token)
    id = int(payload["sub"])

    try:
        session = SessionLocal()

        projects = session.execute(select(Projects.id, Projects.name, Users.username).join(Users, Projects.creator_id == Users.id).order_by(Projects.id.asc())).all()
        secrets_sum = session.execute(select(Projects.id, func.count(Secrets.project_id)).select_from(Projects).outerjoin(Secrets, Projects.id == Secrets.project_id).group_by(Projects.id).order_by(Projects.id.asc())).all()

        if len(projects) == 0:
            raise HTTPException(
                status_code=404,
                detail="No projects found."
            )

        project_list = []

        for index, project in enumerate(projects):

            project_list.append({
                "id": str(project.id),
                "name": project.name,
                "creator": project.username,
                "secrets": str(secrets_sum[index][1])
            })

        return {
            "list": project_list,
            "message": "Loaded projects."
        }

    finally:
        session.close()