from typing import List

from bson import ObjectId as OID
from fastapi import APIRouter, Path, Response, Depends
from fastapi.responses import JSONResponse

from zshort.api.models import auth, requests, responses
from zshort.auth.oauth import get_user
from zshort.db import q
from zshort.db.models import Short

router = APIRouter(prefix="/shorts", tags=["shorts"])


@router.get(
    "/{slug}",
    summary="Get a specific short URL",
    responses={200: {"model": responses.ShortURL}, 404: {"model": responses.ErrorMessage}},
)
async def get_short(slug: str = Path(title="The slug to get")) -> Response:
    if stored := await Short.find_one(q(slug=slug)):
        stored.visits += 1
        await stored.commit()
        return JSONResponse(content=stored.dump())
    return Response(status_code=404, content={"error": "Short URL not found"})


@router.get("/", summary="Get all short URLs", responses={200: {"model": List[responses.ShortURL]}})
async def get_all_shorts(
    page: int = 0, limit: int = 25, user: auth.User = Depends(get_user)
) -> Response:
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    shorts = await Short.find(q(owner=OID(user.id))).to_list(None)
    current_page = shorts[page * limit : (page + 1) * limit]
    result = [x.dump() for x in current_page]
    return JSONResponse(content=result)


@router.post(
    "/",
    summary="Create a short URL",
    status_code=201,
    responses={
        201: {"model": responses.ShortURL},
        401: {"model": responses.ErrorMessage},
        404: {"model": responses.ErrorMessage},
        409: {"model": responses.AlreadyExists},
    },
)
async def create_short(
    request: requests.SlugRequest, user: auth.User = Depends(get_user)
) -> Response:
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    short = Short(
        long_url=request.url, title=request.title, expires_at=request.expires_at, owner=user.id
    )
    if request.slug:
        if existing := await Short.find_one(q(slug=request.slug)):
            return JSONResponse(
                status_code=409,
                content={"error": "Short URL already exists", "short": existing.dump()},
            )
        elif not 3 <= len(request.slug) <= 32:
            return JSONResponse(
                status_code=400, content={"error": "Slug size must be >= 3 and <= 32"}
            )
        short = Short(slug=request.slug, long_url=request.url, title=request.title)

    try:
        await short.commit()
    except Exception as e:
        # Log exception here
        print(e)
        return Response(status_code=500)
    return JSONResponse(status_code=201, content=short.dump())
