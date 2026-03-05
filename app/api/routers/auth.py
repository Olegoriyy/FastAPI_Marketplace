from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy import select

from app.core.security.hashing_password import hashing_password
from app.core.security.jwt_auth import (
    check_and_decode_token,
    create_access_token,
    oauth2_sheme,
)
from app.db.deps import AsyncSession, get_session_tx
from app.models.models import Users
from app.schemas.user import UserCreate, UserLogin, UserPablic

auth_router = APIRouter(tags=['users'])


@auth_router.post('/registr', response_model=UserPablic, status_code=201)
async def registration(
    user: Annotated[UserCreate, Body()],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
) -> UserPablic:
    new_user = Users(
        username=user.username,
        email=user.email,
        hashed_password=hashing_password(user.password),
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return UserPablic.model_validate(new_user)


@auth_router.post('/login')
async def login(
    user: Annotated[UserLogin, Body()],
    session: Annotated[AsyncSession, Depends(get_session_tx)],
):
    stmt = select(Users.id).where(Users.username == user.username)
    user_id = await session.scalar(stmt)

    access_token = create_access_token(user_id)
    return {'status': 'success', 'access_token': access_token}


@auth_router.get('/check_access_token')
async def check_token(token: Annotated[str, Depends(oauth2_sheme)]):
    payload = check_and_decode_token(token)
    return {'payload': payload, 'user_id': payload['user_id']}
