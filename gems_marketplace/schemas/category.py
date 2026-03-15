from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str


class CategoryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
