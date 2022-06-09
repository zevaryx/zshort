import asyncio

import ulid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from zshort.api.models.requests import LoginRequest, RegisterRequest
from zshort.api.models.responses import ErrorMessage, Token
from zshort.db import q
from zshort.db.models import User as DBUser, Invite

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/token", summary="Login", responses={200: {"model": Token}, 401: {"model": ErrorMessage}}
)
async def login(request: LoginRequest) -> Response:
    ph = PasswordHasher()
    user = await DBUser.find_one(q(username=request.username))
    if not user:
        await asyncio.sleep(0.2)  # Force delay
        return JSONResponse(status_code=401, content={"error": "Invalid username/password"})

    try:
        ph.verify(user.hash, request.password)
    except VerifyMismatchError:
        return JSONResponse(status_code=401, content={"error": "Invalid username/password"})

    if ph.check_needs_rehash(user.hash):
        user.hash = ph.hash(request.password)

    if not user.token:
        user.token = ulid.new().str
        await user.commit()

    return JSONResponse(
        status_code=200, content={"access_token": user.token, "token_type": "bearer"}
    )


@router.post(
    "/register",
    summary="Register new account",
    status_code=201,
    responses={201: {"model": Token}, 400: {"model": ErrorMessage}},
)
async def register(request: RegisterRequest) -> Response:
    invite = await Invite.find_one(q(token=request.invite))
    if not invite:
        return JSONResponse(status_code=400, content={"error": "Invite is not valid"})
    elif (invite.max_uses != 0 and invite.uses >= invite.max_use) or not invite.active:
        invite.active = False
        await invite.commit()
        return JSONResponse(status_code=400, content={"error": "Invite is not valid"})

    ph = PasswordHasher()
    user = await DBUser.find_one(q(username=request.username))
    if user:
        return JSONResponse(status_code=400, content={"error": "Username already exists"})

    hash = ph.hash(request.password)
    user = DBUser(
        username=request.username, hash=hash, token=ulid.new().str, used_invite=request.invite
    )
    await user.commit()
    invite.uses += 1
    await invite.commit()
    return JSONResponse(
        status_code=201, content={"access_token": user.token, "token_type": "bearer"}
    )
