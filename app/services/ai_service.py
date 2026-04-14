from openai import AsyncOpenAI

from app.core.config import settings

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

_SYSTEM_PROMPT = (
    "You are a summarization assistant. Write a concise 2-3 sentence summary "
    "of the provided text. Respond in the same language as the content. "
    "Output only the summary — no titles, labels, or extra commentary."
)


async def generate_summary(content: str) -> str:
    response = await _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
