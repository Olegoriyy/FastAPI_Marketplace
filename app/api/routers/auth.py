from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response
from sqlalchemy import select

from app.core.config import settings
from app.core.security.hashing_password import checking_password, hashing_password
from app.core.security.jwt_auth import (
    check_and_decode_access_token,
    check_and_decode_refresh_token,
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
)
from app.db.deps import AsyncSession, get_session_tx
from app.models.models import RefreshSession, Users
from app.schemas.user import UserCreate, UserLogin, UserPublic

auth_router = APIRouter(tags=['auth'])
REFRESH_COOKIE_NAME = 'REFRESH_TOKEN'


def _set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )


def _add_reftoken_to_db(session: AsyncSession, reftoken: str):
    payload = check_and_decode_refresh_token(reftoken)
    ref_token = RefreshSession(
        user_id=payload['user_id'],
        hashed_token=payload['jti'],
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    session.add(ref_token)


@auth_router.post('/register', response_model=UserPublic, status_code=201)
async def registration(
    user: Annotated[UserCreate, Body()],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> UserPublic:
    new_user = Users(
        username=user.username,
        email=user.email,
        hashed_password=hashing_password(user.password),
    )
    session.add(new_user)
    await session.flush()
    await session.refresh(new_user)
    return UserPublic.model_validate(new_user)


@auth_router.post('/login')
async def login(
    user: Annotated[UserLogin, Body()],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    response: Response,
):
    stmt = select(Users).where(Users.username == user.username)
    db_user = await session.scalar(stmt)
    if db_user is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if checking_password(user.password, db_user.hashed_password):
        access_token = create_access_token(db_user.id)
        refresh_token = create_refresh_token(db_user.id)

        _set_refresh_cookie(response, refresh_token)

        _add_reftoken_to_db(session, refresh_token)

        return {'status': 'success', 'access_token': access_token}
    raise HTTPException(status_code=401, detail='Invalid credentials')


@auth_router.get('/user/me', response_model=UserPublic)
async def user_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
):
    payload = check_and_decode_access_token(token)
    user = await session.get(Users, payload['user_id'])
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return UserPublic.model_validate(user)


@auth_router.post('/refresh')
async def refresh(
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    response: Response,
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail='No refresh token cookie')

    payload = check_and_decode_refresh_token(refresh_token)

    old_ref_token = await session.scalar(
        select(RefreshSession).where(RefreshSession.hashed_token == payload['jti'])
    )
    if old_ref_token is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    old_ref_token.revoked_at = datetime.now(timezone.utc)
    new_access_token = create_access_token(payload['user_id'])
    new_ref_token = create_refresh_token(payload['user_id'])

    _set_refresh_cookie(response, new_ref_token)

    _add_reftoken_to_db(session, new_ref_token)

    return {'access_token': new_access_token}
