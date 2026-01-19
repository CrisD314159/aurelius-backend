"""
This module is the entrypoint for the backed of aurelius desktop app
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.text_router import text_router
from app.api.user_router import user_router
from app.api.chats_router import chats_router
from app.api.health_router import health_router
from app.utils.model_loading.model_loading import lifespan


app = FastAPI(
    title="Aurelius Backend",
    description="""This API handles LLM services for aurelius desktop app""",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(text_router)
app.include_router(user_router)
app.include_router(chats_router)
