import os
import re
from datetime import timedelta

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import Role, Users
from backend.helpers import now, raise_error

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
encryption_key = os.getenv("ENCRYPTION_KEY")

if secret_key is None:
    raise RuntimeError(500, "An error occured. Please try again.")

if encryption_key is None:
    raise RuntimeError(500, "An error occured. Please try again.")

password_hash = PasswordHash.recommended()
fernet = Fernet(encryption_key)


def email_valid(email: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", email))


def password_strong(password: str) -> bool:
    has_char = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(not char.isalnum() for char in password)
    is_long = len(password) > 8

    return has_char and has_digit and has_symbol and is_long


def check_credentials(email: str, password: str, confirm: str) -> None:
    if not email_valid(email):
        raise_error(400, "Invalid email.")

    if confirm != password:
        raise_error(400, "Passwords do not match.")

    if not password_strong(password):
        raise_error(
            422,
            "Password must have at least one character, digit, symbol and must be more than 8 characters long.",
        )


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
    token = jwt.encode(
        data,
        secret_key,
        algorithm="HS256",
    )

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
        select(Users.id).where(Users.id == user_id)
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
