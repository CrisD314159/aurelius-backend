"""
 This class implements schemas using pydantic for data transmission
"""

from pydantic import BaseModel


class ElectronPrompt(BaseModel):
    """For frontent prompt"""
    prompt: str


class ModelAnswer(BaseModel):
    """To return the LLM answer to the frontend"""
    answer: str


class UserSetup(BaseModel):
    """To register the local user for the first time"""
    user_name: str
    model: str
