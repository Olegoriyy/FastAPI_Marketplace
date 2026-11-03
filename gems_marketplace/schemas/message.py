from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    chat_id: int
    first_user_id: int
    second_user_id: int | None
    text: str | None
