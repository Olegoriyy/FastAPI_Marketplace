from typing import Annotated

from fastapi import APIRouter, Body, Depends

from gems_marketplace.dependencies import (
    get_user_service,
)
from gems_marketplace.schemas.user import UserPublic
from gems_marketplace.services.user_service import UserService

users_router = APIRouter(tags=["users"])


@users_router.get("/user/{user_id}", response_model=UserPublic, status_code=200)
async def get_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserPublic:
    user_from_db = await user_service.get_by_id(user_id)
    return UserPublic.model_validate(user_from_db)


@users_router.post("/user", response_model=UserPublic, status_code=200)
async def get_user_by_name(
    user_name: Annotated[str, Body(embed=True)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserPublic:
    user_from_db = await user_service.get_by_name(user_name)
    return UserPublic.model_validate(user_from_db)


# в Аутентификации это есть ужно переделать
# @users_router.post('/user/add', response_model=UserPublic, status_code=201)
# async def user_add(
#     user: Annotated[UserCreate, Body],
#     user_service: Annotated[UserService, Depends(get_user_service)],
# ) -> UserPublic:
#     user = await user_service.add_in_db(user)
#     return UserPublic.model_validate(user)


@users_router.delete("/user/delete/{user_id}", status_code=204)
async def delete_user(
    user_id: int, user_service: Annotated[UserService, Depends(get_user_service)]
) -> None:
    return await user_service.delete_by_id(user_id)
