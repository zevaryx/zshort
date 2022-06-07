import ulid
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from zshort.api.models import auth, requests, responses
from zshort.auth.oauth import get_user
from zshort.db import q
from zshort.db.models import Invite

router = APIRouter(prefix="/invites", tags=["invites"])


@router.post(
    "/",
    summary="Create invite",
    status_code=201,
    responses={
        201: {"model": responses.InviteResponse},
        400: {"model": responses.ErrorMessage},
        401: {"model": responses.ErrorMessage},
        403: {"model": responses.ErrorMessage},
    },
)
async def create_invite(
    request: requests.InviteRequest, user: auth.User = Depends(get_user)
) -> Response:
    if not user or user.disabled:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    invites = await Invite.find(q(owner=user.id, valid=True)).to_list(None)
    if len(invites) >= user.max_invites and not user.admin:
        return JSONResponse(
            status_code=403, content={"error": "Max number of active invites reached"}
        )
    if request.max_uses < 0:
        return JSONResponse(status_code=400, content={"error": "Requested uses is invalid"})

    invite = Invite(owner=user.id, token=ulid.new().str, max_uses=request.max_uses)
    await invite.commit()
    return JSONResponse(status_code=201, content={"invite": invite.token})
