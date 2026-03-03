from typing import Annotated

from fastapi import Body, FastAPI

from app.core.security.hashing_password import checking_password, hashing_password
from app.db.sessions import async_session_factory
from app.models.models import Users
from app.schemas.user import UserCreate, UserPablic

app = FastAPI()


@app.post('/registration', response_model=UserPablic, status_code=201)
async def registration(user: Annotated[UserCreate, Body()]):
    async with async_session_factory() as session:
        new_user = Users(
            username=user.username,
            email=user.email,
            hashed_password=hashing_password(user.password),
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return UserPablic.model_validate(new_user)


@app.get('/user/{user_id}', response_model=UserPablic, status_code=200)
async def get_user(user_id: int) -> UserPablic:
    async with async_session_factory() as session:
        user_from_db = await session.get(Users, user_id)
        return UserPablic.model_validate(user_from_db)
