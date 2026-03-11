from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str


class CategoryPublic(BaseModel):
    id: int
    name: str
