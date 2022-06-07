import logging
import os
from datetime import datetime
from hashlib import sha3_224

import ulid
from argon2 import PasswordHasher
from dotenv import load_dotenv
from fastapi import FastAPI, Path, Response
from fastapi.responses import RedirectResponse

from zshort.api.v1 import router
from zshort.db import connect, q
from zshort.db.models import Short, User

app = FastAPI(title="ZShorts")
app.include_router(router)

load_dotenv()
logger = logging.getLogger(__name__)


@app.get("/{slug}", include_in_schema=False)
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
    if len(await User.find().to_list(None)) == 0:
        h = sha3_224()
        h.update(datetime.now().isoformat().encode("UTF8"))
        pwd = h.hexdigest()
        ph = PasswordHasher()
        hash = ph.hash(pwd)
        user = User(username="admin", hash=hash, admin=True)
        await user.commit()
        logger.info("No users found, default user created. Credentials saved in default.txt")
        with open("default.txt", "w+") as f:
            data = f"Username: {user.username}\nPassword: {pwd}\nToken: {user.token}"
            f.write(data)
