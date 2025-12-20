"""
This module contains a class that handles all the http chat methods
"""

from app.db.init_db import AureliusDB


class ChatsService:
    """
    This class contains all the methods for http chat services
    """

    def __init__(self):
        self.database = AureliusDB()

    def get_user_chats(self):
        """
        Returns all the stored chats
        """
        chats = self.database.get_user_chats()
        return chats

    def get_user_chat_content(self, chat_id):
        """
        Returns all the stored content from one chat
        """
        chat_content = self.database.get_chat_content(chat_id=chat_id)
        return chat_content
