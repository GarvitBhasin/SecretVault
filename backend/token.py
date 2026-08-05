from jose import jwt
from datetime import datetime, timezone, timedelta


def generate_token(data: dict):
    expiry = datetime.now(timezone.utc) + timedelta(hours=2)

    to_encode = data.copy()
    to_encode.update({
        "expiry": expiry.timestamp()
    })

    token = jwt.encode(
        to_encode, "LEO-UBC-2008", algorithm="HS256"
    )

    return token