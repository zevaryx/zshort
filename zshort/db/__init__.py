from datetime import timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks import MotorAsyncIOInstance

from zshort.util import find

DB_INST = MotorAsyncIOInstance()


def connect(host: str, username: str, password: str, port: int = 27017, uri: str = None) -> None:
    """
    Connect to MongoDB.

    Args:
        host: Hostname/IP
        username: Username
        password: Password
        port: Port
    """
    global DB_INST
    if uri:
        client = AsyncIOMotorClient(uri)
    else:
        client = AsyncIOMotorClient(
            host=host,
            username=username,
            password=password,
            port=port,
            tz_aware=True,
            tzinfo=timezone.utc,
        )
    db = client.zshort
    DB_INST.set_db(db)


QUERY_OPS = ["ne", "lt", "lte", "gt", "gte", "not", "in", "nin", "mod", "all", "size"]
STRING_OPS = [
    "exact",
    "iexact",
    "contains",
    "icontains",
    "startswith",
    "istartswith",
    "endswith",
    "iendswith",
    "wholeword",
    "iwholeword",
    "regex",
    "iregex" "match",
]
GEO_OPS = [
    "get_within",
    "geo_within_box",
    "geo_within_polygon",
    "geo_within_center",
    "geo_within_sphere",
    "geo_intersects",
    "near",
    "within_distance",
    "within_spherical_distance",
    "near_sphere",
    "within_box",
    "within_polygon",
    "max_distance",
    "min_distance",
]

ALL_OPS = QUERY_OPS + STRING_OPS + GEO_OPS


def q(**kwargs: dict) -> dict:
    """uMongo query wrapper."""  # noqa: D403
    query = {}
    for key, value in kwargs.items():
        if key == "_id":
            value = ObjectId(value)
        elif "__" in key:
            args = key.split("__")
            if not any(x in ALL_OPS for x in args):
                key = ".".join(args)
            else:
                idx = args.index(find(lambda x: x in ALL_OPS, args))
                key = ".".join(args[:idx])
                value = {f"${args[idx]}": value}
        query[key] = value
    return query
