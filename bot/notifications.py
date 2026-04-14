import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from bot.config import TELEGRAM_BOT_TOKEN
from bot.services.subscription_service import get_author_subscribers

logger = logging.getLogger(__name__)


async def notify_subscribers(post: Post, db: AsyncSession) -> None:
    subscribers = await get_author_subscribers(db, post.author_id)
    if not subscribers:
        return

    summary_text = post.summary if post.summary else "No summary available."

    notification = (
        f"📝 <b>New post by {post.author.username}</b>\n\n"
        f"<b>{post.title}</b>\n\n"
        f"{summary_text}"
    )

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        for subscription in subscribers:
            try:
                await bot.send_message(
                    chat_id=subscription.telegram_chat_id,
                    text=notification,
                    parse_mode="HTML",
                )
            except Exception:
                logger.warning(
                    "Failed to notify chat_id=%s for post_id=%s",
                    subscription.telegram_chat_id,
                    post.id,
                )
    finally:
        await bot.session.close()
