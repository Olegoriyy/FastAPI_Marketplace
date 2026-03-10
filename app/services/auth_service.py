from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update, values
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.hashing_password import checking_password, hashing_password
from app.core.security.jwt_auth import (
    check_and_decode_access_token,
    check_and_decode_refresh_token,
    create_access_token,
    create_refresh_token,
)
from app.models.models import RefreshSession, User
from app.repositories.refresh_sessions import (
    add_reftoken_to_db,
    get_ref_session_from_db_by_jti,
)
from app.repositories.roles import get_role_by_name
from app.repositories.users import (
    add_user_in_db,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.user import UserCreate, UserLogin, UserPublic


async def revoke_all_user_ref_sessions(db_user: User, session: AsyncSession):
    await session.execute(
        update(RefreshSession)
        .where(
            RefreshSession.user_id == db_user.id,
            RefreshSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )


async def user_registration(
    user: UserCreate,
    session: AsyncSession,
) -> UserPublic:
    db_user = await get_user_by_username(session, user.username)
    if db_user is not None:
        raise HTTPException(status_code=409, detail='user already registered')

    db_user = await get_user_by_email(session, user.email)
    if db_user is not None:
        raise HTTPException(status_code=409, detail='user already registered')
    buyer_role = await get_role_by_name('buyer', session)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashing_password(user.password),
        role_id=buyer_role.id,
    )
    await add_user_in_db(session, new_user)
    await session.flush()
    await session.refresh(new_user)
    return new_user


async def login_user(user: UserLogin, session: AsyncSession):
    db_user = await get_user_by_username(session, user.username)
    if db_user is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if not checking_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    await revoke_all_user_ref_sessions(db_user, session)

    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)
    ref_session_id = await add_reftoken_to_db(session, refresh_token)

    result = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'ref_session_id': ref_session_id,
    }
    return result


async def check_and_get_user_by_token(
    token: str,
    session: AsyncSession,
):
    payload = check_and_decode_access_token(token)
    user = await session.get(User, payload['user_id'])
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return user


async def refresh_and_get_tokens(
    refresh_token: str | None,
    session: AsyncSession,
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail='No refresh token cookie')
    now = datetime.now(timezone.utc)
    payload = check_and_decode_refresh_token(refresh_token)

    db_session = await get_ref_session_from_db_by_jti(payload['jti'], session=session)
    if db_session is None:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if db_session.revoked_at is not None:
        raise HTTPException(status_code=401, detail='Token revoked')

    if db_session.expires_at <= now:
        db_session.revoked_at = now
        raise HTTPException(status_code=401, detail='Refresh token expired')

    user = await session.get(User, payload['user_id'])
    if user is None or not user.is_active:
        db_session.revoked_at = now
        raise HTTPException(status_code=401, detail='User is inactive or not found')

    db_session.revoked_at = now

    new_access_token = create_access_token(payload['user_id'])
    new_ref_token = create_refresh_token(payload['user_id'])

    new_ref_session_id = await add_reftoken_to_db(session, new_ref_token)

    result = {
        'access_token': new_access_token,
        'ref_token': new_ref_token,
        'ref_session_id': new_ref_session_id,
    }

    return result


async def revoke_current_ref_token(
    token: str,
    session: AsyncSession,
):
    payload = check_and_decode_refresh_token(token)
    ref_token = await get_ref_session_from_db_by_jti(
        jti=payload['jti'], session=session
    )
    ref_token.revoked_at = datetime.now(timezone.utc)
    return True
