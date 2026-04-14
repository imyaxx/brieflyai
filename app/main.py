from contextlib import asynccontextmanager
from typing import AsyncGenerator

import logging

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("BrieflyAI starting up")
    yield
    logger.info("BrieflyAI shutting down")


app = FastAPI(title="BrieflyAI", version="1.0.0", lifespan=lifespan)

app.include_router(api_v1_router, prefix="/api/v1")
