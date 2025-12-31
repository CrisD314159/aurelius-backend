"""
This module contains a router for http chat methods
"""

from fastapi import APIRouter, Depends
from app.services.chats.chats_service import ChatsService


chats_router = APIRouter()


@chats_router.get("/chats/getChats")
def get_user_chats(chat_service: ChatsService = Depends()):
    """
    Returns all the user chats
    """

    chats = chat_service.get_user_chats()
    return {"success": True, "message": chats}


@chats_router.get("/chats/getChatContent/{chat_id}")
def get_chat_content(chat_id: int, chat_service: ChatsService = Depends()):
    """
    Gets the chat contents
    """
    messages = chat_service.get_user_chat_content(chat_id=chat_id)
    response = {"chat_id": chat_id, "messages": messages}
    return {"success": True, "message": response}


@chats_router.delete("/chats/{chat_id}")
def delete_chat(chat_id: int, chat_service: ChatsService = Depends()):
    """
    Deletes a chat from the local database
    """
    chat_service.delete_chat(chat_id=chat_id)
    return {"success": True, "message": "Chat deleted successfully"}
