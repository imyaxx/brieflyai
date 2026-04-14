import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.start import router as start_router
from bot.handlers.subscriptions import router as subscriptions_router

logging.basicConfig(level=logging.INFO)


async def start_polling() -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dispatcher = Dispatcher()

    dispatcher.include_router(start_router)
    dispatcher.include_router(subscriptions_router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_polling())
