from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.posts import router as posts_router

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "ok"})


router.include_router(auth_router)
router.include_router(posts_router)
# router.include_router(users_router)
