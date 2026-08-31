import requests


def create_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def send_request(method, endpoint, headers=None, payload=None):
    return requests.request(
        method, f"http://127.0.0.1:8000{endpoint}", headers=headers, json=payload
    )
