from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    hash: str
    token: str
    admin: bool
    max_invites: int
