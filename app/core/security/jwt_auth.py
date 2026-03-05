from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

oauth2_sheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(user_id: int):
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user_id,
        'exp': int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


def check_and_decode_token(acces_token):
    return jwt.decode(acces_token, SECRET_KEY, ALGORITHM)
