from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.core.security import hashing_password
from app.db.deps import AsyncSession, get_session_tx
from app.models.models import Users
from app.schemas.user import UserCreate, UserLogin, UserPablic

users_router = APIRouter(tags=['users'])


@users_router.get('/user/{user_id}', response_model=UserPablic, status_code=200)
async def get_user(
    user_id: int, session: Annotated[AsyncSession, Depends(get_session_tx)]
) -> UserPablic:
    user_from_db = await session.get(Users, user_id)
    return UserPablic.model_validate(user_from_db)
