from typing import List

from bson import ObjectId as OID
from fastapi import APIRouter, Path, Response, Depends
from fastapi.responses import JSONResponse

from zshort.api.models import auth, requests, responses
from zshort.auth.oauth import get_user
from zshort.db import q
from zshort.db.models import Short, get_now

main_router = APIRouter(prefix="/short", tags=["shorts"])
sub_router = APIRouter(prefix="/shorts", tags=["shorts"])


@main_router.get(
    "/{slug}",
    summary="Get a specific short URL",
    responses={200: {"model": responses.ShortURL}, 404: {"model": responses.ErrorMessage}},
)
async def get_short(slug: str = Path(title="The slug to get")) -> Response:
    if stored := await Short.find_one(q(slug=slug)):
        stored.visits += 1
        await stored.commit()
        return JSONResponse(content=stored.dump())
    return JSONResponse(status_code=404, content={"error": "Short URL not found"})


@main_router.delete(
    "/{slug}",
    summary="Delete a short URL",
    status_code=204,
    responses={
        401: {"model": responses.ErrorMessage},
        404: {"model": responses.ErrorMessage},
    },
)
async def delete_short(
    slug: str = Path(title="The slug to delete"), user: auth.User = Depends(get_user)
) -> Response:
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    if short := await Short.find_one(q(slug=slug)):
        if str(short.owner) == user.id:
            await short.delete()
            return Response(status_code=204)
        else:
            return JSONResponse(status_code=403, content={"error": "You do not own this short"})
    return JSONResponse(status_code=404, content={"error": "Short not found"})


@main_router.patch(
    "/{slug}",
    summary="Edit a short URL",
    status_code=200,
    responses={
        200: {"model": responses.ShortURL},
        400: {"model": responses.ErrorMessage},
        401: {"model": responses.ErrorMessage},
        403: {"model": responses.ErrorMessage},
        404: {"model": responses.ErrorMessage},
        409: {"model": responses.AlreadyExists},
    },
)
async def patch_short(
    request: requests.SlugPatchRequest,
    user: auth.User = Depends(get_user),
    slug: str = Path(title="The slug to delete"),
) -> Response:
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    short = await Short.find_one(q(slug=slug))
    if not short:
        return JSONResponse(status_code=404, content={"error": "Short not found"})
    elif str(short.owner) != user.id:
        return JSONResponse(status_code=403, content={"error": "You do not own this short"})
    elif not any(x for x in request.__dict__.values()):
        return JSONResponse(status_code=400, content={"error": "Empty update"})

    if request.slug and (existing := await Short.find_one(q(slug=slug))):
        return JSONResponse(
            status_code=409, content={"error": "Short URL already exists", "short": existing.dump()}
        )

    if request.url:
        short.long_url = request.url
    if request.slug:
        short.slug = request.slug
    if request.title:
        short.title = request.title
    if request.expires_at:
        short.expires_at = request.expires_at

    short.edited_at = get_now()

    await short.commit()
    return JSONResponse(status_code=200, content=short.dump())


@sub_router.get(
    "/", summary="Get all short URLs", responses={200: {"model": List[responses.ShortURL]}}
)
async def get_all_shorts(
    page: int = 0, limit: int = 25, user: auth.User = Depends(get_user)
) -> Response:
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    shorts = await Short.find(q(owner=OID(user.id))).to_list(None)
    current_page = shorts[page * limit : (page + 1) * limit]
    result = [x.dump() for x in current_page]
    return JSONResponse(content=result)


@main_router.post(
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
        short = Short(slug=request.slug, long_url=request.url, title=request.title, owner=user.id)

    try:
        await short.commit()
    except Exception as e:
        # Log exception here
        print(e)
        return Response(status_code=500)
    return JSONResponse(status_code=201, content=short.dump())
