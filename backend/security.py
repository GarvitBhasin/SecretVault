from jose import jwt, JWTError
from datetime import timedelta
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import select
from backend.models import Users
from backend.helpers import raise_error, now
import os, re
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

def email_valid(email):
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", email))

def password_strong(password):
    has_char = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(not char.isalnum() for char in password)
    is_long = len(password) > 8

    return True if has_char and has_digit and has_symbol and is_long else False

def encode_token(data: dict):

    # Generate expiry and add to data
    expiry = now() + timedelta(minutes=45)

    data.update({
        "exp": expiry.timestamp()
    })

    # encode and return token
    token = jwt.encode(
        data, secret_key, algorithm="HS256"
    )

    return token

def verify_user(token, session):

    # Decode token for user_id and expiry; raise error if invalid/expired.
    try:
        payload = jwt.decode(
            token, secret_key, algorithms=["HS256"]
        )
    except JWTError as error:
        raise_error(401, "Invalid or expired token.")

    # Check if user exists in db and return user if found
    user_id = int(payload["sub"])

    user = session.execute(
        select(Users.id).where(Users.id == user_id)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return user_id