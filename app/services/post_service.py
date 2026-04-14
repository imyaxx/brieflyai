import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from app.services.ai_service import generate_summary


async def create_post(db: AsyncSession, author_id: uuid.UUID, data: PostCreate) -> Post:
    summary = await generate_summary(data.content)
    post = Post(
        title=data.title,
        content=data.content,
        summary=summary,
        author_id=author_id,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post(db: AsyncSession, post_id: uuid.UUID) -> Post:
    post = await db.scalar(select(Post).where(Post.id == post_id))
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found.",
        )
    return post


async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Post]:
    result = await db.scalars(
        select(Post)
        .where(Post.is_published.is_(True))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.all())


async def get_user_posts(db: AsyncSession, author_id: uuid.UUID) -> list[Post]:
    result = await db.scalars(
        select(Post)
        .where(Post.author_id == author_id)
        .order_by(Post.created_at.desc())
    )
    return list(result.all())


async def update_post(
    db: AsyncSession,
    post_id: uuid.UUID,
    author_id: uuid.UUID,
    data: PostUpdate,
) -> Post:
    post = await get_post(db, post_id)

    if post.author_id != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this post.",
        )

    changes = data.model_dump(exclude_unset=True)

    if "content" in changes:
        changes["summary"] = await generate_summary(changes["content"])

    for field, value in changes.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(
    db: AsyncSession,
    post_id: uuid.UUID,
    author_id: uuid.UUID,
) -> None:
    post = await get_post(db, post_id)

    if post.author_id != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this post.",
        )

    await db.delete(post)
    await db.commit()
