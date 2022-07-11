from pydantic import BaseModel
from typing import Optional
from pydantic.networks import EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshToken(BaseModel):
    refresh_token: str