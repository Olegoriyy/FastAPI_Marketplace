from datetime import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.deps import get_session_tx
from app.models.base import Base

PkInt = Annotated[int, mapped_column(primary_key=True)]
CreatedAt = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
]


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[PkInt]
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[CreatedAt]
    refresh_session: Mapped[list['RefreshSession']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=True)
    role: Mapped['Roles'] = relationship(back_populates='user')


class RefreshSession(Base):
    __tablename__ = 'refresh_sessions'

    id: Mapped[PkInt]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user: Mapped['Users'] = relationship(back_populates='refresh_session')
    hashed_token: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    created_at: Mapped[CreatedAt]
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[None | datetime] = mapped_column(
        DateTime(timezone=True),
    )


class Roles(Base):
    __tablename__ = 'roles'

    id: Mapped[PkInt]
    name: Mapped[str] = mapped_column(unique=True)
    user: Mapped['Users'] = relationship(back_populates='role')
