from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security.jwt_auth import check_and_decode_refresh_token
from app.models.models import RefreshSession


async def get_ref_session_from_db_by_jti(jti: str, session: AsyncSession):
    ref_session = await session.scalar(
        select(RefreshSession).where(
            RefreshSession.hashed_token == jti,
        )
    )

    return ref_session


async def add_reftoken_to_db(session: AsyncSession, reftoken: str):
    payload = check_and_decode_refresh_token(reftoken)
    ref_session = RefreshSession(
        user_id=payload['user_id'],
        hashed_token=payload['jti'],
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    session.add(ref_session)
    await session.flush()
    await session.refresh(ref_session)
    return ref_session.id
