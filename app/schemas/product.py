from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    title: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    quantity: int
