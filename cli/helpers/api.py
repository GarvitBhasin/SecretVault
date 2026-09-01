from typing import Any

import requests
from requests import Response


def create_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def send_request(
    method: str,
    endpoint: str,
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
) -> Response:
    return requests.request(
        method, f"http://127.0.0.1:8000{endpoint}", headers=headers, json=payload
    )
