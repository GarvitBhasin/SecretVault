from jose import jwt, JWTError
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy import select
from backend.database import Users, Role
from backend.helpers import raise_error, now
from cryptography.fernet import Fernet
from pwdlib import PasswordHash
import os, re
load_dotenv()

secret_key = os.getenv("SECRET_KEY")
encryption_key = os.getenv("ENCRYPTION_KEY")

password_hash = PasswordHash.recommended()
fernet = Fernet(encryption_key)

def email_valid(email):
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", email))

def password_strong(password):
    has_char = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(not char.isalnum() for char in password)
    is_long = len(password) > 8

    return True if has_char and has_digit and has_symbol and is_long else False

def check_credentials(email, password, confirm):
    if not email_valid(email):
        raise_error(400, "Invalid email.")

    if confirm != password:
        raise_error(400, "Passwords do not match.")

    if not password_strong(password):
        raise_error(422, "Password must have at least one character, digit, symbol and must be more than 8 characters long.")

def hash_password(password):
    return password_hash.hash(password)

def verify_password(password, hash):
    return password_hash.verify(password, hash)

def encode_token(data: dict):

    # Generate expiry and add to data
    expiry = now() + timedelta(minutes=45)

    data.update({
        "exp": expiry.timestamp()
    })

    # encode and return token
    token = jwt.encode(
        data, secret_key, algorithm="HS256",
    )

    return token

def verify_user(token, session):

    # Decode token for user_id and expiry; raise error if invalid/expired.
    try:
        payload = jwt.decode(
            token, secret_key, algorithms=["HS256"]
        )
    except (JWTError, KeyError, ValueError):
        raise_error(401, "Invalid or expired token.")

    # Check if user exists in db and return user if found
    user_id = int(payload["sub"])

    user = session.execute(
        select(Users.id)
        .where(Users.id == user_id)
    ).scalar_one_or_none()

    if user is None:
        raise_error(404, "User not found.")

    return user_id

def validate_user(session, user_id, minimum_access_level):

    # Extract user's role
    role = session.execute(
        select(Users.role)
        .where(Users.id == user_id)
    ).scalar_one_or_none()

    # Check if role's access level is lower than allowed
    if Role[role.upper()].value < minimum_access_level.value:
        raise_error(403, "Access not granted. Please request admin/owner for access")

def encrypt(plaintext):
    return fernet.encrypt(plaintext.encode()).decode()

def decrypt(ciphertext):
    return fernet.decrypt(ciphertext.encode()).decode()