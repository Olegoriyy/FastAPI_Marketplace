from typing import Annotated

from fastapi import APIRouter, Body, Depends

from gems_marketplace.core.security.jwt_auth import oauth2_scheme
from gems_marketplace.dependencies import (
    get_auth_service,
    get_user_service,
)
from gems_marketplace.schemas.user import UserPrivate, UserPublic
from gems_marketplace.services.auth_service import AuthService
from gems_marketplace.services.user_service import UserService

users_router = APIRouter(tags=["users"])


@users_router.get("/user/{user_id}/profile", response_model=UserPublic, status_code=200)
async def check_user_by_id(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserPublic:
    user_from_db = await user_service.get_by_id(user_id)
    return UserPublic.model_validate(user_from_db)


@users_router.post("/user", response_model=UserPublic, status_code=200)
async def check_user_by_username(
    username: Annotated[str, Body(embed=True)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserPublic:
    user_from_db = await user_service.get_by_username(username)
    return UserPublic.model_validate(user_from_db)


@users_router.get("/user/me", response_model=UserPrivate)
async def user_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserPrivate:
    user = await auth_service.check_and_get_user_by_token(token)
    return UserPrivate.model_validate(user)


@users_router.delete("/user/me", status_code=204)
async def delete_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    user = await auth_service.check_and_get_user_by_token(token)
    return await user_service.delete(user)
