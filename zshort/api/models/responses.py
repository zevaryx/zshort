from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ShortURL(BaseModel):
    id: str
    long_url: str
    slug: str
    title: Optional[str] = None
    visits: int
    created_at: datetime
    edited_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    owner: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ErrorMessage(BaseModel):
    error: str


class AlreadyExists(ErrorMessage):
    short: ShortURL


class InviteResponse(BaseModel):
    invite: str
