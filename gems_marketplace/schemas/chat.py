from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Chat(BaseModel):
    type: Literal[
        "ai",
        "support",
        "seller",
        "ai,support",
    ]
    chat_id: int | None
    product_id: int | None
    first_user_id: int = Field(gt=0)
    second_user_id: int | None
