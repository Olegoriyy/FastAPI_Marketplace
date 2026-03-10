from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.fields import CreatedAt, PkInt, UpdatedAt


class RefreshSession(Base):
    __tablename__ = 'refresh_sessions'

    id: Mapped[PkInt]
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), index=True
    )
    user: Mapped['User'] = relationship(back_populates='refresh_session')
    hashed_token: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    created_at: Mapped[CreatedAt]
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[None | datetime] = mapped_column(DateTime(timezone=True))


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[PkInt]
    name: Mapped[str] = mapped_column(unique=True)
    user: Mapped[list['User']] = relationship(back_populates='role')


class User(Base):
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
    role: Mapped['Role'] = relationship(back_populates='user')
    products: Mapped[list['Product']] = relationship(back_populates='seller')


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[PkInt]

    seller: Mapped['User'] = relationship(back_populates='products')
    seller_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False, index=True
    )

    category: Mapped['Category'] = relationship(back_populates='products')
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id'),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[PkInt]
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    products: Mapped[list['Product']] = relationship(back_populates='category')
