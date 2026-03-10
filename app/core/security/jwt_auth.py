from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

ACCESS_SECRET_KEY = settings.ACCESS_SECRET_KEY
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES


def create_access_token(user_id: int):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user_id,
        'exp': int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, ACCESS_SECRET_KEY, ALGORITHM)


def check_and_decode_access_token(acces_token):
    try:
        return jwt.decode(acces_token, ACCESS_SECRET_KEY, ALGORITHM)
    except:
        raise HTTPException(status_code=401, detail='Unauthorized')


def create_refresh_token(user_id: int):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user_id,
        'exp': int((now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)).timestamp()),
        'jti': uuid4().hex,
    }
    return jwt.encode(payload, REFRESH_SECRET_KEY, ALGORITHM)


def check_and_decode_refresh_token(refresh_token):
    return jwt.decode(refresh_token, REFRESH_SECRET_KEY, ALGORITHM)
