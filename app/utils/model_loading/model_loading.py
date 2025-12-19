"""
This module initializes on the background
 all the required dependencies before app startup
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.stt.stt_config import STTConfig
from app.services.stt.stt_service import STTService
from app.services.llm.llm_service import LLMService
from app.db.init_db import AureliusDB

aurelius_models = {}
database_instances = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt_config = STTConfig()
    stt_service = STTService(config=stt_config)
    llm_service = LLMService()
    aurelius_models["stt"] = stt_service
    aurelius_models["llm"] = llm_service
    yield
    aurelius_models.clear()
