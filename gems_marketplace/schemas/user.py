from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=128, pattern=r"\S")
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class UserPrivate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role_id: int


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=128, pattern=r"\S")
    password: str = Field(min_length=8, max_length=128)
