from typing import Annotated, Any

from fastapi import APIRouter, Body, Cookie, Depends, Response

from gems_marketplace.config import settings
from gems_marketplace.core.security.jwt_auth import oauth2_scheme
from gems_marketplace.dependencies import get_auth_service
from gems_marketplace.schemas.user import UserCreate, UserLogin, UserPublic
from gems_marketplace.services.auth_service import AuthService

auth_router = APIRouter(tags=["auth"])
REFRESH_COOKIE_NAME = "REFRESH_TOKEN"


async def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )


@auth_router.post("/register", response_model=UserPublic, status_code=201)
async def registration(
    user: Annotated[UserCreate, Body()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserPublic:
    user_in_db = await auth_service.user_registration(user)
    return UserPublic.model_validate(user_in_db)


@auth_router.post("/login")
async def login(
    user: Annotated[UserLogin, Body()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> dict[str, Any]:
    result = await auth_service.login_user(user)
    await _set_refresh_cookie(response, result["refresh_token"])
    return result


@auth_router.get("/user/me", response_model=UserPublic)
async def user_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserPublic:
    user = await auth_service.check_and_get_user_by_token(token)
    return UserPublic.model_validate(user)


@auth_router.post("/refresh")
async def refresh(
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> dict[str, Any]:
    result = await auth_service.refresh_and_get_tokens(refresh_token)

    await _set_refresh_cookie(response, result["ref_token"])

    return {"access_token": result["access_token"]}


@auth_router.post("/logout")
async def logout(
    token: Annotated[str, Cookie(alias=REFRESH_COOKIE_NAME)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> dict[str, str]:
    await auth_service.logout(token)
    response.delete_cookie(key="REFRESH_TOKEN")
    return {"status": "logout complete"}
