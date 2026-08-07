from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, ForeignKey, create_engine
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DB_URL")
engine = create_engine(database_url)

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

class IDRequest(BaseModel):
    token: str
    id: str