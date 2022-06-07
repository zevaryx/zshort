from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from zshort.api.models.auth import User
from zshort.db import q
from zshort.db.models import User as DBUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_user(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    user = await DBUser.find_one(q(token=token))
    if user:
        return User(**user.dump())
    return None
