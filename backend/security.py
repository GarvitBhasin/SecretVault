from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import select
from backend.models import Users
import os
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

def encode_token(data: dict):

    # Generate expiry and add to data
    expiry = datetime.now(timezone.utc) + timedelta(minutes=45)

    to_encode = data.copy()
    to_encode.update({
        "exp": expiry.timestamp()
    })

    # encode and return token
    token = jwt.encode(
        to_encode, secret_key, algorithm="HS256"
    )

    return token

def raise_error(code, detail):
    raise HTTPException(
        status_code=code,
        detail=detail
    )

def verify_user(token, session):

    # decode token for user_id and expiry; raise error if invalid/expired.
    try:
        payload = jwt.decode(
            token, secret_key, algorithms=["HS256"]
        )
    except JWTError:
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