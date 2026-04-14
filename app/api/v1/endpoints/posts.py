import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.post_service import (
    create_post,
    delete_post,
    get_post,
    get_posts,
    get_user_posts,
    update_post,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=201)
async def create(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await create_post(db, current_user.id, data)
    return PostResponse.model_validate(post)


@router.get("/my", response_model=list[PostResponse])
async def list_my_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    posts = await get_user_posts(db, current_user.id)
    return [PostResponse.model_validate(post) for post in posts]


@router.get("", response_model=list[PostResponse])
async def list_published_posts(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    posts = await get_posts(db, skip=skip, limit=limit)
    return [PostResponse.model_validate(post) for post in posts]


@router.get("/{post_id}", response_model=PostResponse)
async def get_single_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await get_post(db, post_id)
    return PostResponse.model_validate(post)


@router.put("/{post_id}", response_model=PostResponse)
async def update(
    post_id: uuid.UUID,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await update_post(db, post_id, current_user.id, data)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=204)
async def delete(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await delete_post(db, post_id, current_user.id)
