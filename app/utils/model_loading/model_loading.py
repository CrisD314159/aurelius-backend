from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.services.stt.stt_config import STTConfig
from app.services.stt.stt_service import STTService
from app.services.llm.llm_service import LLMService

aurelius_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt_config = STTConfig()
    stt_service = STTService(config=stt_config)
    llm_service = LLMService()
    aurelius_models["stt"] = stt_service
    aurelius_models["llm"] = llm_service
    yield
    aurelius_models.clear()
