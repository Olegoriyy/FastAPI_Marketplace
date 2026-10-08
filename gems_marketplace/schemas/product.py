from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=3000)
    price: Decimal = Field(max_digits=10, decimal_places=2)
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
    title: str
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0)
    category_id: int = Field(gt=0)
