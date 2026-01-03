"""
This module initializes on the background
 all the required dependencies before app startup
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
import sys
import os


aurelius_models = {}
database_instances = {}

_initialized = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _initialized

    # Prevent re-initialization in any child process or frozen executable
    if _initialized:
        yield
        return

    # Check if running as PyInstaller executable
    is_frozen = getattr(sys, 'frozen', False)

    # Skip if this is not the main process
    if hasattr(sys, '_called_from_test') or (os.environ.get('WORKER_PROCESS') and not os.environ.get('MAIN_PROCESS')):
        yield
        return

    # For PyInstaller, only initialize once
    if is_frozen and _initialized:
        yield
        return

    # Import only when lifespan actually runs (after freeze_support)
    print("Starting model initialization...")

    # Prevent re-initialization in child processes
    if hasattr(sys, '_called_from_test') or os.environ.get('WORKER_PROCESS'):
        yield
        return

    from app.services.stt.stt_config import STTConfig
    from app.services.stt.stt_service import STTService
    from app.services.llm.llm_service import LLMService
    from app.services.tts.tts_kokoro_service import TTSKokoroService

    stt_config = STTConfig()
    stt_service = STTService(config=stt_config)
    tts_service = TTSKokoroService()
    llm_service = LLMService(tts_service=tts_service)
    aurelius_models["stt"] = stt_service
    aurelius_models["llm"] = llm_service

    _initialized = True
    print("Model initialization complete.")

    yield
    print("Shutting down models...")
    aurelius_models.clear()
    _initialized = False
