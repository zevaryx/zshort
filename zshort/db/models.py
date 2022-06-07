from datetime import datetime, timezone
from typing import Optional

import nanoid
import ulid
from umongo import Document, fields

from zshort.db import DB_INST


def get_now() -> datetime:
    """Get proper timestamp."""
    return datetime.now(tz=timezone.utc)


def generate_nanoid(size: int = 12) -> str:
    return nanoid.generate(size=size)


def generate_ulid() -> str:
    return ulid.new().str


@DB_INST.register
class Short(Document):
    long_url: str = fields.URLField(required=True)
    slug: str = fields.StringField(default=generate_nanoid)
    title: Optional[str] = fields.StringField(required=False, default=None)
    visits: int = fields.IntegerField(default=0)
    created_at: datetime = fields.DateTimeField(default=get_now)
    edited_at: Optional[datetime] = fields.DateTimeField(default=None)
    expires_at: Optional[datetime] = fields.DateTimeField(default=None)
    owner: str = fields.ObjectIdField()


@DB_INST.register
class User(Document):
    username: str = fields.StringField(unique=True)
    email: Optional[str] = fields.EmailField(default=None)
    full_name: Optional[str] = fields.StringField(default=None)
    disabled: bool = fields.BooleanField(default=False)
    hash: str = fields.StringField()
    token: str = fields.StringField(default=generate_ulid)
    admin: bool = fields.BooleanField(default=False)
    max_invites: int = fields.BooleanField(default=5)
    used_invite: Optional[str] = fields.StringField(default=None)


@DB_INST.register
class Invite(Document):
    owner: str = fields.ObjectIdField()
    token: str = fields.StringField(default=generate_ulid)
    uses: int = fields.IntegerField(default=0)
    max_uses: int = fields.IntegerField(default=5)
    active: bool = fields.BooleanField(default=True)
