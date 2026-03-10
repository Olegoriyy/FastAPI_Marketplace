from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class LogoutResponse(BaseModel):
    status: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
