from typing import Annotated, Any

from fastapi import APIRouter, Body, Cookie, Depends, Response

from gems_marketplace.config import settings
from gems_marketplace.core.security.jwt_auth import oauth2_scheme
from gems_marketplace.db.deps import AsyncSession, get_session_tx
from gems_marketplace.schemas.user import UserCreate, UserLogin, UserPublic
from gems_marketplace.services.auth_service import (
    check_and_get_user_by_token,
    login_user,
    refresh_and_get_tokens,
    revoke_current_ref_token,
    user_registration,
)

auth_router = APIRouter(tags=['auth'])
REFRESH_COOKIE_NAME = 'REFRESH_TOKEN'


async def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )


@auth_router.post('/register', response_model=UserPublic, status_code=201)
async def registration(
    user: Annotated[UserCreate, Body()],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> UserPublic:
    user_public = await user_registration(user, session)
    return UserPublic.model_validate(user_public)


@auth_router.post('/login')
async def login(
    user: Annotated[UserLogin, Body()],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    response: Response,
) -> dict[str, Any]:
    result = await login_user(user, session)
    await _set_refresh_cookie(response, result['refresh_token'])
    return result


@auth_router.get('/user/me', response_model=UserPublic)
async def user_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> UserPublic:
    user = await check_and_get_user_by_token(token, session)
    return UserPublic.model_validate(user)


@auth_router.post('/refresh')
async def refresh(
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    response: Response,
) -> dict[str, Any]:
    result = await refresh_and_get_tokens(refresh_token, session)

    await _set_refresh_cookie(response, result['ref_token'])

    return {'access_token': result['access_token']}


@auth_router.post('/logout')
async def logout(
    token: Annotated[str, Cookie(alias=REFRESH_COOKIE_NAME)],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
    response: Response,
) -> dict[str, str]:
    await revoke_current_ref_token(token, session)
    response.delete_cookie(key='REFRESH_TOKEN')
    return {'status': 'logout complete'}
