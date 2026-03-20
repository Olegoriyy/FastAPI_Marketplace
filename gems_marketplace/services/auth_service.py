from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from gems_marketplace.config import settings
from gems_marketplace.contracts.repositories import (
    RefreshSessionRepository,
    RoleRepository,
    UserRepository,
)
from gems_marketplace.core.security.hashing_password import (
    checking_password,
    hashing_password,
)
from gems_marketplace.core.security.jwt_auth import (
    check_and_decode_access_token,
    check_and_decode_refresh_token,
    create_access_token,
    create_refresh_token,
)
from gems_marketplace.models.models import RefreshSession, User
from gems_marketplace.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        ref_session_repo: RefreshSessionRepository,
    ) -> None:
        self.session = session
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.ref_sesion_repo = ref_session_repo

    # Регистрация
    async def user_registration(self, user: UserCreate) -> User:
        db_user = await self.user_repo.get_by_name(user.username)
        if db_user is not None:
            raise HTTPException(status_code=409, detail="user already registered")

        db_user = await self.user_repo.get_by_email(user.email)
        if db_user is not None:
            raise HTTPException(status_code=409, detail="user already registered")

        buyer_role = await self.role_repo.get_by_name("buyer")
        if buyer_role is None:
            raise HTTPException(status_code=404, detail=("buyer-role not found"))

        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashing_password(user.password),
            role_id=buyer_role.id,
        )
        await self.user_repo.add_in_db(new_user)
        await self.session.flush()
        await self.session.refresh(new_user)
        return new_user

    # Логин, Выдача токенов

    async def login_user(self, user: UserLogin) -> dict[str, Any]:
        db_user = await self.user_repo.get_by_name(user.username)
        if db_user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not checking_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        await self._revoke_all_user_ref_sessions(db_user)

        access_token = create_access_token(db_user.id)
        refresh_token = create_refresh_token(db_user.id)

        ref_session = await self._create_ref_session_by_ref_token(refresh_token)

        await self.ref_sesion_repo.add_in_db(ref_session)
        await self.session.flush()
        await self.session.refresh(ref_session)

        result = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "ref_session_id": ref_session.id,
        }
        return result

    async def check_and_get_user_by_token(
        self,
        token: str,
    ) -> User:
        payload = check_and_decode_access_token(token)
        user = await self.user_repo.get_by_id(user_id=payload["user_id"])
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user

    async def refresh_and_get_tokens(
        self,
        refresh_token: str | None,
    ) -> dict[str, Any]:
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token cookie")
        now = datetime.now(timezone.utc)
        payload = check_and_decode_refresh_token(refresh_token)

        db_session = await self.ref_sesion_repo.get_by_jti(payload["jti"])
        if db_session is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if db_session.revoked_at is not None:
            raise HTTPException(status_code=401, detail="Token revoked")

        if db_session.expires_at <= now:
            db_session.revoked_at = now
            raise HTTPException(status_code=401, detail="Refresh token expired")

        user = await self.user_repo.get_by_id(payload["user_id"])
        if user is None or not user.is_active:
            db_session.revoked_at = now
            raise HTTPException(status_code=401, detail="User is inactive or not found")

        db_session.revoked_at = now

        new_access_token = create_access_token(payload["user_id"])
        new_ref_token = create_refresh_token(payload["user_id"])

        ref_session = await self._create_ref_session_by_ref_token(new_ref_token)

        await self.ref_sesion_repo.add_in_db(ref_session)
        await self.session.flush()
        await self.session.refresh(ref_session)

        result = {
            "access_token": new_access_token,
            "ref_token": new_ref_token,
            "ref_session_id": ref_session.id,
        }

        return result

    async def logout(
        self,
        token: str,
    ) -> None:
        payload = check_and_decode_refresh_token(token)
        ref_session = await self.ref_sesion_repo.get_by_jti(jti=payload["jti"])
        if ref_session is None:
            raise HTTPException(status_code=404, detail=("ref_session not found"))
        ref_session.revoked_at = datetime.now(timezone.utc)

    ###### доп функции для упрощения
    async def _revoke_all_user_ref_sessions(self, db_user: User) -> None:
        await self.session.execute(
            update(RefreshSession)
            .where(
                RefreshSession.user_id == db_user.id,
                RefreshSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def _create_ref_session_by_ref_token(self, token: str) -> RefreshSession:
        payload = check_and_decode_refresh_token(token)
        ref_session = RefreshSession(
            user_id=payload["user_id"],
            hashed_token=payload["jti"],
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        )
        return ref_session
