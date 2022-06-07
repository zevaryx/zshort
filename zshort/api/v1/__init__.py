from fastapi import APIRouter

from zshort.api.v1 import auth, invites, shorts

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(invites.router)
router.include_router(shorts.main_router)
router.include_router(shorts.sub_router)
