import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription


async def get_or_create_subscription(
    db: AsyncSession,
    subscriber_id: uuid.UUID,
    author_id: uuid.UUID,
    telegram_chat_id: str,
) -> Subscription:
    existing = await db.scalar(
        select(Subscription).where(
            Subscription.subscriber_id == subscriber_id,
            Subscription.author_id == author_id,
        )
    )
    if existing:
        return existing

    subscription = Subscription(
        subscriber_id=subscriber_id,
        author_id=author_id,
        telegram_chat_id=telegram_chat_id,
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return subscription


async def remove_subscription(
    db: AsyncSession,
    subscriber_id: uuid.UUID,
    author_id: uuid.UUID,
) -> None:
    subscription = await db.scalar(
        select(Subscription).where(
            Subscription.subscriber_id == subscriber_id,
            Subscription.author_id == author_id,
        )
    )
    if subscription is None:
        return

    await db.delete(subscription)
    await db.commit()


async def get_author_subscribers(
    db: AsyncSession,
    author_id: uuid.UUID,
) -> list[Subscription]:
    result = await db.scalars(
        select(Subscription).where(
            Subscription.author_id == author_id,
            Subscription.telegram_chat_id.is_not(None),
        )
    )
    return list(result.all())
