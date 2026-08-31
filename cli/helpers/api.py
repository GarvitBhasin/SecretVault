import os

import requests

backend_url = os.getenv("APP_URL")


def create_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def send_request(method, endpoint, headers=None, payload=None):
    return requests.request(
        method, f"{backend_url}{endpoint}", headers=headers, json=payload
    )
