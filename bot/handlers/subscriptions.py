from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User
from bot.keyboards import subscription_keyboard
from bot.services.subscription_service import get_or_create_subscription, remove_subscription

router = Router()


async def _get_author_by_username(db: AsyncSession, username: str) -> User | None:
    return await db.scalar(select(User).where(User.username == username))


@router.message(Command("subscribe"))
async def handle_subscribe(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /subscribe <author_username>")
        return

    author_username = parts[1].strip()

    async with AsyncSessionLocal() as db:
        author = await _get_author_by_username(db, author_username)
        if author is None:
            await message.answer(f"Author <b>{author_username}</b> not found.", parse_mode="HTML")
            return

        subscriber_telegram_id = str(message.from_user.id)

        if str(author.id) == subscriber_telegram_id:
            await message.answer("You cannot subscribe to yourself.")
            return

        subscriber = await db.scalar(
            select(User).where(User.email == f"tg:{message.from_user.id}")
        )

        if subscriber is None:
            await message.answer(
                "Your Telegram account is not linked to a BrieflyAI account.\n"
                "Please register at the platform first."
            )
            return

        await get_or_create_subscription(
            db=db,
            subscriber_id=subscriber.id,
            author_id=author.id,
            telegram_chat_id=str(message.chat.id),
        )

    await message.answer(
        f"✅ You are now subscribed to <b>{author_username}</b>.\n"
        "You will receive a notification when they publish a new post.",
        parse_mode="HTML",
        reply_markup=subscription_keyboard(author_username),
    )


@router.message(Command("unsubscribe"))
async def handle_unsubscribe(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /unsubscribe <author_username>")
        return

    author_username = parts[1].strip()

    async with AsyncSessionLocal() as db:
        author = await _get_author_by_username(db, author_username)
        if author is None:
            await message.answer(f"Author <b>{author_username}</b> not found.", parse_mode="HTML")
            return

        subscriber = await db.scalar(
            select(User).where(User.email == f"tg:{message.from_user.id}")
        )
        if subscriber is None:
            await message.answer("Your Telegram account is not linked to a BrieflyAI account.")
            return

        await remove_subscription(db=db, subscriber_id=subscriber.id, author_id=author.id)

    await message.answer(
        f"You have unsubscribed from <b>{author_username}</b>.",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("unsubscribe:"))
async def handle_unsubscribe_callback(callback: CallbackQuery) -> None:
    author_username = callback.data.split(":", 1)[1]

    async with AsyncSessionLocal() as db:
        author = await _get_author_by_username(db, author_username)
        if author is None:
            await callback.answer("Author not found.", show_alert=True)
            return

        subscriber = await db.scalar(
            select(User).where(User.email == f"tg:{callback.from_user.id}")
        )
        if subscriber is None:
            await callback.answer("Account not linked.", show_alert=True)
            return

        await remove_subscription(db=db, subscriber_id=subscriber.id, author_id=author.id)

    await callback.answer(f"Unsubscribed from {author_username}.")
    await callback.message.edit_reply_markup(reply_markup=None)
