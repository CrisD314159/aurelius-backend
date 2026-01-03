"""
This module initializes on the background
 all the required dependencies before app startup
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI


aurelius_models = {}
database_instances = {}


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Import only when lifespan actually runs (after freeze_support)
    print("Starting model initialization...")

    from app.services.llm.llm_service import LLMService

    llm_service = LLMService()
    aurelius_models["llm"] = llm_service

    _initialized = True
    print("Model initialization complete.")

    yield
    print("Shutting down models...")
    aurelius_models.clear()
    _initialized = False
