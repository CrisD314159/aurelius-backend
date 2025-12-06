"""
This module is the entrypoint for the backed of aurelius desktop app
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.call_router import router as call_router
from app.api.user_router import user_router

app = FastAPI(
    title="Aurelius Backend",
    description="""This API handles everithing related to TTS, STT
    and LLM services for aurelius desktop app""",
    version="1.0.0"
)

origins = [
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(call_router)
app.include_router(user_router)
