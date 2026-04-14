from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "👋 Welcome to <b>BrieflyAI</b>!\n\n"
        "I notify you when authors you follow publish new posts — "
        "with an AI-generated summary so you can decide if it's worth reading.\n\n"
        "To subscribe to an author, send:\n"
        "<code>/subscribe &lt;author_username&gt;</code>",
        parse_mode="HTML",
    )
