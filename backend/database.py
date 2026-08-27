from sqlalchemy.orm import sessionmaker, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Text, DateTime, ForeignKey, create_engine
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from enum import Enum
import os

load_dotenv()
database_url = os.getenv("DB_URL")
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

# DB TABLES

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False)

class Role(Enum):
    VIEWER = 1
    ADMIN = 2
    OWNER = 3

class Projects(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class Secrets(Base):
    __tablename__ = "secrets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class Logs(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(25), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(25), nullable=False)
    asset_id: Mapped[int] = mapped_column(nullable=False)
    action_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expiry: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class Action(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class Asset(str, Enum):
    ACCOUNT = "ACCOUNT"
    PROJECT = "PROJECT"
    SECRET = "SECRET"

Base.metadata.create_all(engine)

# REQUEST TEMPLATES

class InitRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm: str

class AddRequest(BaseModel):
    token: str
    username: str
    email: str
    password: str
    confirm: str
    role: int

class ResetPasswordRequest(BaseModel):
    password: str
    confirm: str
    token: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenRequest(BaseModel):
    token: str

class CreateProjectRequest(BaseModel):
    token: str
    name: str

class IDRequest(BaseModel):
    token: str
    id: int

class EditProjectRequest(BaseModel):
    token: str
    id: int
    name: str

class EditUserRequest(BaseModel):
    token: str
    id: int
    role: int

class SecretRequest(BaseModel):
    token: str
    id: int
    name: str
    value: str
    description: str | None = None