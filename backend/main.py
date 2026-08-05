from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, sessionmaker
from sqlalchemy import String, create_engine, select
from pydantic import BaseModel
from pwdlib import PasswordHash
from backend.token import *

app = FastAPI()
engine = create_engine("postgresql+psycopg://postgres:shalom%4002@localhost:5432/securevault")
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

@app.post("/register", status_code=201)
def register(data: RegisterRequest):

    # Check password pairs
    if data.confirm != data.password:
        raise HTTPException(
            status_code=400,
            detail="Confirm password does not match original password"
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
                detail="Email is already registered"
            ) 
        if existing_username:
            raise HTTPException(
                status_code=409,
                detail="Username taken"
            ) 

        # Check password strength
        has_char = any(char.isalpha() for char in data.password)
        has_digit = any(char.isdigit() for char in data.password)
        has_symbol = any(not char.isalnum() for char in data.password)
        is_long = len(data.password) > 8

        if not (has_char and has_digit and has_symbol and is_long):
            raise HTTPException(
                status_code=422,
                detail="Password must have at least one character, digit, symbol and be more than 8 characters long"
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

        id = session.execute(select(Users.id).where(Users.email == data.email)).scalar_one()

        token = generate_token({ "sub": str(id) })
                
        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Account created successfully"
        }
    except Exception as e:
        session.rollback()
        print("ERROR:", e)
        raise
    finally:
        session.close()

@app.post("/login", status_code=200)
def login(data: LoginRequest):

    try:
        session = SessionLocal()

        result = session.execute(select(Users.password_hash, Users.id).where(Users.email == data.email)).first()

        if result is None:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        stored_hash, id = result

        is_valid = password_hash.verify(data.password, stored_hash)

        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        token = generate_token({ "sub": str(id) })
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "message": "Successfully logged in."
        }
    finally:
        session.close()