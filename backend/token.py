from jose import jwt
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
load_dotenv()

secret_key = os.getenv("SECRET_KEY")

def encode_token(data: dict):
    expiry = datetime.now(timezone.utc) + timedelta(minutes=45)

    to_encode = data.copy()
    to_encode.update({
        "expiry": expiry.timestamp()
    })

    token = jwt.encode(
        to_encode, secret_key, algorithm="HS256"
    )

    return token

def decode_token(token: str):

    payload = jwt.decode(
        token, secret_key, algorithms=["HS256"]
    )

    return payload