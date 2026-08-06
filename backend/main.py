from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from sqlalchemy import String, create_engine, select, delete
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
            detail="Confirm password does not match original password."
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
            username=data.username,
            email=data.email,
            password_hash=hashed_pass,
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
            "message": "Account created successfully."
        }
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.post("/login", status_code=200)
def login(data: LoginRequest):

    try:
        session = SessionLocal()

        # find user in db with corelating hash and id
        result = session.execute(select(Users.password_hash, Users.id).where(Users.email == data.email)).first()

        if result is None:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        stored_hash, id = result

        # Check if password is correct
        is_valid = password_hash.verify(data.password, stored_hash)

        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        # Return token and message
        token = encode_token({ "sub": str(id) })
        
        return {
            "token": token,
            "token_type": "bearer",
            "message": "Successfully logged in."
        }
    finally:
        session.close()

@app.post("/me", status_code=200)
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

@app.delete("/delete")
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
            "message": "Account successfully deleted."
        }
    except:
        session.rollback()
        raise
    finally:
        session.close()