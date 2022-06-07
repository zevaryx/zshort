import os

from dotenv import load_dotenv
from fastapi import FastAPI, Path, Response
from fastapi.responses import RedirectResponse

from zshort.api.v1 import router
from zshort.db import connect, q
from zshort.db.models import Short

app = FastAPI(title="ZShorts")
app.include_router(router)

load_dotenv()


@app.get("/{slug}")
async def redirect(slug: str = Path(title="The slug to get")) -> Response:
    short = await Short.find_one(q(slug=slug))
    if short:
        short.visits += 1
        await short.commit()
        return RedirectResponse(url=short.long_url)
    return Response(status_code=404)


@app.on_event("startup")
async def startup():
    host = os.environ.get("MONGO_HOST")
    user = os.environ.get("MONGO_USER")
    password = os.environ.get("MONGO_PASS")
    port = os.environ.get("MONGO_PORT", 27017)
    uri = os.environ.get("MONGO_URI")
    connect(host=host, username=user, password=password, port=port, uri=uri)
