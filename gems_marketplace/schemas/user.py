from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(max_length=128)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role_id: int


class UserLogin(BaseModel):
    username: str = Field(max_length=128)
    password: str = Field(min_length=8, max_length=128)
