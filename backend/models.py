from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://postgres:shalom@02@localhost:5432/securevault")

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(25), nullable=False)

class RegisterRequest(Base):
    id: int
    username: str
    email: str
    password: str
    role: str

class Secrets(Base):
    pass

Base.metadata.create_all(engine)