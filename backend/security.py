import re
from datetime import timedelta

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Role, Users
from backend.helpers import get_env_var, now, raise_error

load_dotenv()

secret_key = get_env_var("SECRET_KEY")
encryption_key = get_env_var("ENCRYPTION_KEY")

password_hash = PasswordHash.recommended()
fernet = Fernet(encryption_key)


def check_input(password, email=None, confirm=None, role=None):
    # Email validity
    if email is not None:
        if bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", email)):
            raise_error(422, "Invalid email")

    if confirm is not None:
        if password != confirm:
            raise_error(400, "Password pairs do not match.")

    # Password strength
    has_char = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(not char.isalnum() for char in password)
    is_long = len(password) > 8

    if not (has_char and has_digit and has_symbol and is_long):
        raise_error(
            422,
            """Password must have at least one character, digit,
            symbol and must be more than 8 characters long.""",
        )

    # Role validity
    if role is not None:
        try:
            Role(role)
        except ValueError:
            raise_error(422, "Invalid role.")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hash: str) -> None:
    if not password_hash.verify(password, hash):
        raise_error(401, "Incorrect email or password.")


def encode_token(data: dict) -> str:

    # Generate expiry and add to data
    expiry = now() + timedelta(minutes=45)

    data.update({"exp": expiry.timestamp()})

    # encode and return token
    token = jwt.encode(data, secret_key, algorithm="HS256")

    return token


def verify_user(token: str, session: Session) -> Users:

    # Decode token for user_id and expiry
    # Check for expired/invalid/tampered token or malformed sub
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise_error(401, "Invalid or expired token.")

    # Check if user exists in db and return user if found
    user = session.execute(
        select(Users).where(Users.id == user_id)
    ).scalar_one_or_none()

    if user is None:
        raise_error(404, "User not found.")

    return user


def validate_user(session: Session, user: Users, minimum_access_level: Role) -> None:

    # Check if role's access level is lower than allowed
    if Role[user.role].value < minimum_access_level.value:
        raise_error(403, "Access not granted. Please request admin/owner for access")


def encrypt(plaintext: str) -> str:
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return fernet.decrypt(ciphertext.encode()).decode()
