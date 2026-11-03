from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255, pattern=r"\S")
    description: str = Field(min_length=1, max_length=3000)
    price: Decimal = Field(max_digits=10, decimal_places=2, ge=0)
    quantity: int = Field(ge=0)
    category_id: int = Field(gt=0)


class ProductPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    category_id: int
    title: str
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    quantity: int
    published: bool


class ProductUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255, pattern=r"\S")
    description: str | None = None
    price: Decimal | None = Field(default=None, max_digits=10, decimal_places=2, ge=0)
    quantity: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)
