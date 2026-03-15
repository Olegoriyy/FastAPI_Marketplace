from typing import Annotated

from fastapi import APIRouter, Depends

from gems_marketplace.db.deps import AsyncSession, get_session_tx
from gems_marketplace.repositories.users import get_user_by_id
from gems_marketplace.schemas.user import UserPublic

users_router = APIRouter(tags=["users"])


@users_router.get("/user/{user_id}", response_model=UserPublic, status_code=200)
async def get_user(
    user_id: int, session: Annotated[AsyncSession, Depends(get_session_tx)]
) -> UserPublic:
    user_from_db = await get_user_by_id(session, user_id)
    return UserPublic.model_validate(user_from_db)
