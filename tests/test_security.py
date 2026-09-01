from datetime import timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from backend.database import Role
from backend.helpers import now
from backend.security import (
    check_input,
    decrypt,
    encode_token,
    encrypt,
    hash_password,
    secret_key,
    validate_user,
    verify_password,
    verify_user,
)

# Password hashing


def test_password_is_hashed():
    password = "Password@123"

    hashed_password = hash_password(password)

    assert hashed_password != password


def test_correct_password_is_verified():
    password = "Password@123"
    hashed_password = hash_password(password)

    verify_password(password, hashed_password)


def test_incorrect_password_is_rejected():
    hashed_password = hash_password("Password@123")

    with pytest.raises(HTTPException) as exc:
        verify_password("WrongPassword@123", hashed_password)

    assert exc.value.status_code == 401


def test_same_password_produces_different_hashes():
    password = "Password@123"

    assert hash_password(password) != hash_password(password)


# Input validation


def test_matching_strong_password_is_accepted():
    check_input(
        password="Password@123",
        confirm="Password@123",
    )


def test_passwords_that_do_not_match_are_rejected():
    with pytest.raises(HTTPException) as exc:
        check_input(
            password="Password@123",
            confirm="Different@123",
        )

    assert exc.value.status_code == 400


@pytest.mark.parametrize(
    "password",
    [
        "short1!",
        "onlyletters",
        "123456789",
        "Password123",
        "Password!",
        "123456789!",
    ],
)
def test_weak_passwords_are_rejected(password):
    with pytest.raises(HTTPException) as exc:
        check_input(password)

    assert exc.value.status_code == 422


@pytest.mark.parametrize(
    "password",
    [
        "Password@123",
        "Strong!Pass1",
        "Test1234#",
    ],
)
def test_strong_passwords_are_accepted(password):
    check_input(password)


@pytest.mark.parametrize(
    "role",
    [
        Role.VIEWER.value,
        Role.ADMIN.value,
        Role.OWNER.value,
    ],
)
def test_valid_roles_are_accepted(role):
    check_input(
        password="Password@123",
        role=role,
    )


@pytest.mark.parametrize(
    "role",
    [
        -1,
        100,
        999,
    ],
)
def test_invalid_roles_are_rejected(role):
    with pytest.raises(HTTPException) as exc:
        check_input(
            password="Password@123",
            role=role,
        )

    assert exc.value.status_code == 422


# Encryption


def test_value_is_encrypted():
    plaintext = "Secret message"

    ciphertext = encrypt(plaintext)

    assert ciphertext != plaintext


def test_encrypted_value_can_be_decrypted():
    plaintext = "Secret message"

    ciphertext = encrypt(plaintext)

    assert decrypt(ciphertext) == plaintext


def test_same_plaintext_produces_different_ciphertext():
    plaintext = "Secret message"

    assert encrypt(plaintext) != encrypt(plaintext)


# JWT


def test_token_is_created():
    token = encode_token({"sub": "1"})

    assert isinstance(token, str)
    assert token


def test_token_contains_correct_user_id():
    token = encode_token({"sub": "123"})

    payload = jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
    )

    assert payload["sub"] == "123"


def test_token_contains_expiry():
    token = encode_token({"sub": "123"})

    payload = jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
    )

    assert "exp" in payload


def test_valid_token_returns_user(db_session, viewer):
    token = encode_token({"sub": str(viewer.id)})

    user = verify_user(token, db_session)

    assert user.id == viewer.id


def test_tampered_token_is_rejected(db_session, viewer):
    token = encode_token({"sub": str(viewer.id)})

    parts = token.split(".")
    parts[1] += "tampered"
    tampered_token = ".".join(parts)

    with pytest.raises(HTTPException) as exc:
        verify_user(tampered_token, db_session)

    assert exc.value.status_code == 401


def test_expired_token_is_rejected(db_session, viewer):
    expired_token = jwt.encode(
        {
            "sub": str(viewer.id),
            "exp": (now() - timedelta(minutes=1)).timestamp(),
        },
        secret_key,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc:
        verify_user(expired_token, db_session)

    assert exc.value.status_code == 401


def test_token_with_invalid_user_id_is_rejected(db_session):
    token = encode_token({"sub": "invalid"})

    with pytest.raises(HTTPException) as exc:
        verify_user(token, db_session)

    assert exc.value.status_code == 401


def test_token_for_nonexistent_user_is_rejected(db_session):
    token = encode_token({"sub": "999999"})

    with pytest.raises(HTTPException) as exc:
        verify_user(token, db_session)

    assert exc.value.status_code == 404


# RBAC


@pytest.mark.parametrize(
    ("user_fixture", "minimum_role"),
    [
        ("viewer", Role.ADMIN),
        ("viewer", Role.OWNER),
        ("admin", Role.OWNER),
    ],
)
def test_insufficient_role_is_rejected(request, user_fixture, minimum_role):
    user = request.getfixturevalue(user_fixture)

    with pytest.raises(HTTPException) as exc:
        validate_user(user, minimum_role)

    assert exc.value.status_code == 403


@pytest.mark.parametrize(
    ("user_fixture", "minimum_role"),
    [
        ("viewer", Role.VIEWER),
        ("admin", Role.VIEWER),
        ("admin", Role.ADMIN),
        ("owner", Role.VIEWER),
        ("owner", Role.ADMIN),
        ("owner", Role.OWNER),
    ],
)
def test_sufficient_role_is_accepted(request, user_fixture, minimum_role):
    user = request.getfixturevalue(user_fixture)

    validate_user(user, minimum_role)
