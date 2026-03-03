from typing import Annotated

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

pk_int = Annotated[int, mapped_column(primary_key=True)]


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[pk_int]
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(
        String(320), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str]
