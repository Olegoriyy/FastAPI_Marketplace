from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException

from gems_marketplace.core.security.jwt_auth import (
    ACCESS_SECRET_KEY,
    ALGORITHM,
    REFRESH_SECRET_KEY,
    check_and_decode_access_token,
    check_and_decode_refresh_token,
    create_access_token,
    create_refresh_token,
)


### Access token tests
def test_correct_encode_and_decode_access_token():
    user_id = 10
    access_token = create_access_token(user_id)

    payload = check_and_decode_access_token(access_token)
    assert payload["user_id"] == user_id


def test_invalid_access_token_returns_401():

    with pytest.raises(HTTPException) as exc_info:
        check_and_decode_access_token("invalid-token")

    assert exc_info.value.status_code == 401


def test_expired_access_token_return_401():
    now = datetime.now(timezone.utc)
    user_id = 10
    payload = {"user_id": user_id, "exp": int((now - timedelta(minutes=5)).timestamp())}
    access_token = jwt.encode(payload, ACCESS_SECRET_KEY, ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        check_and_decode_access_token(access_token)

    assert exc_info.value.status_code == 401


def test_access_token_with_invalid_signature_returns_401():
    now = datetime.now(timezone.utc)
    user_id = 10
    payload = {"user_id": user_id, "exp": int((now + timedelta(minutes=5)).timestamp())}
    access_token = jwt.encode(
        payload, "wrong-secret-key-for-jwt-tests-1234567890", ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        check_and_decode_access_token(access_token)

    assert exc_info.value.status_code == 401


### Refresh token tests
def test_correct_encode_and_decode_refresh_token():
    user_id = 10

    refresh_token = create_refresh_token(user_id)

    payload = check_and_decode_refresh_token(refresh_token)

    assert payload["user_id"] == user_id
    assert payload["jti"] != ""


def test_invalid_refresh_token_returns_401():

    with pytest.raises(HTTPException) as exc_info:
        check_and_decode_refresh_token("invalid-token")

    assert exc_info.value.status_code == 401


def test_expired_refresh_token_returns_401():
    now = datetime.now(timezone.utc)
    user_id = 10
    payload = {
        "user_id": user_id,
        "exp": int((now - timedelta(minutes=5)).timestamp()),
        "jti": uuid4().hex,
    }

    refresh_token = jwt.encode(
        payload,
        REFRESH_SECRET_KEY,
        ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        check_and_decode_refresh_token(refresh_token)

    assert exc_info.value.status_code == 401


def test_refresh_token_with_invalid_signature_returns_401():
    now = datetime.now(timezone.utc)
    user_id = 10
    payload = {
        "user_id": user_id,
        "exp": int((now + timedelta(minutes=5)).timestamp()),
        "jti": uuid4().hex,
    }
    refresh_token = jwt.encode(
        payload, "wrong-secret-key-for-jwt-tests-1234567890", ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        check_and_decode_refresh_token(refresh_token)

    assert exc_info.value.status_code == 401
