from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SlugRequest(BaseModel):
    url: str
    slug: Optional[str] = None
    title: Optional[str] = None
    expires_at: Optional[datetime] = None


class SlugPatchRequest(BaseModel):
    url: Optional[str] = None
    slug: Optional[str] = None
    title: Optional[str] = None
    expires_at: Optional[datetime] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(LoginRequest):
    invite: str


class InviteRequest(BaseModel):
    max_uses: Optional[int] = 5
