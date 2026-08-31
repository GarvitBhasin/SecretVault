from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from backend.database import Role
from backend.helpers import now
from backend.security import (
    check_credentials,
    decrypt,
    encode_token,
    encrypt,
    hash_password,
    secret_key,
    validate_user,
    verify_password,
    verify_user,
)

TEST_VALUE = "batman"

# Hashing


def test_value_is_hashed():
    assert hash_password(TEST_VALUE) != TEST_VALUE


def test_hash_is_verified():
    stored_hash = hash_password(TEST_VALUE)
    assert verify_password(TEST_VALUE, stored_hash) is True


def test_hash_is_not_verified():
    stored_hash = hash_password(TEST_VALUE)
    assert verify_password("abcd", stored_hash) is False


def test_same_passwords_return_diff_hash():
    assert hash_password(TEST_VALUE) != hash_password(TEST_VALUE)


# Encryption


def test_value_is_encrypted():
    assert TEST_VALUE != encrypt(TEST_VALUE)


def test_decrypt_encrypted_data():
    encrypted = encrypt(TEST_VALUE)
    assert decrypt(encrypted) == TEST_VALUE


def test_encrypting_same_data_returns_diff_ciphertext():
    assert encrypt(TEST_VALUE) != encrypt(TEST_VALUE)


# Input Validation


@pytest.mark.parametrize(
    "credentials",
    [
        {
            "email": "email@gmail.com",
            "password": "pass@1234",
            "confirm": "anotherpass@1234",
        },
        {"email": "email@gmail.com", "password": "weak", "confirm": "weak"},
        {"email": "invalid", "password": "abcd@1234", "confirm": "abcd@1234"},
    ],
)
def test_reject_invalid_credentials(credentials):
    with pytest.raises(HTTPException) as exception:
        check_credentials(
            credentials["email"], credentials["password"], credentials["confirm"]
        )

    assert exception.value.status_code == 400 or exception.value.status_code == 422


def test_accept_valid_credentials():
    check_credentials("email@gmail.com", "password@1234", "password@1234")


# JWT


def test_valid_token_is_verified(db_session, viewer):
    token = encode_token({"sub": str(viewer.id)})

    user_id = verify_user(token, db_session)

    assert user_id == viewer.id


def test_token_is_created():
    token = encode_token({"sub": "1"})

    assert isinstance(token, str)
    assert token


def test_token_contains_user_id():
    token = encode_token({"sub": "123"})

    payload = jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
    )

    assert payload["sub"] == "123"


def test_tampered_token(db_session, viewer):
    token = encode_token({"sub": str(viewer.id)})

    parts = token.split(".")
    parts[1] += "wrongtoken"
    tampered_token = ".".join(parts)

    with pytest.raises(HTTPException) as exc:
        verify_user(tampered_token, db_session)

    assert exc.value.status_code == 401


def test_expired_token_rejected(db_session, viewer):
    token = jwt.encode(
        {
            "sub": str(viewer.id),
            "exp": (now() - timedelta(minutes=1)).timestamp(),
        },
        secret_key,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc:
        verify_user(token, db_session)

    assert exc.value.status_code == 401


# RBAC


def test_rbac_access_not_permitted(db_session, viewer, admin):
    with pytest.raises(HTTPException) as exception:
        validate_user(db_session, viewer.id, Role.OWNER)

    assert exception.value.status_code == 403

    with pytest.raises(HTTPException) as exception:
        validate_user(db_session, admin.id, Role.OWNER)

    assert exception.value.status_code == 403


def test_rbac_access_permitted(db_session, viewer, admin, owner):
    validate_user(db_session, viewer.id, Role.VIEWER)
    validate_user(db_session, admin.id, Role.ADMIN)
    validate_user(db_session, owner.id, Role.OWNER)
